import bpy
import gpu
from gpu_extras.batch import batch_for_shader


def _srgb_to_linear(c):
    c = max(0.0, min(1.0, c))
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

class PAINT_OT_lr_screen_color_picker(bpy.types.Operator):
    """Pick a color from the screen with neutral color management (sRGB, Standard, no look, exposure 0, gamma 1)"""
    bl_idname = "lr.screen_color_picker"
    bl_label = "Screen Color Picker"
    bl_options = {'REGISTER', 'UNDO'}

    all_slots: bpy.props.BoolProperty(  # type: ignore
        name="All Material Slots",
        description="Reroute the Color input in all material slots of the active object, not only the active one",
        default=True,
    )

    _draw_handler = None
    _color = None

    @classmethod
    def poll(cls, context):
        return context.mode in {'PAINT_TEXTURE', 'PAINT_VERTEX'} and context.area.type == 'VIEW_3D'

    def _store_color_management(self, scene):
        vs, ds = scene.view_settings, scene.display_settings
        self._cm = {
            'display_device': ds.display_device,
            'view_transform': vs.view_transform,
            'look': vs.look,
            'exposure': vs.exposure,
            'gamma': vs.gamma,
        }

    def _set_neutral_color_management(self, scene):
        vs, ds = scene.view_settings, scene.display_settings
        for obj, attr, value in (
            (ds, 'display_device', 'sRGB'),
            (vs, 'view_transform', 'Standard'),
            (vs, 'look', 'None'),
        ):
            try:
                setattr(obj, attr, value)
            except TypeError:
                pass
        vs.exposure = 0.0
        vs.gamma = 1.0

    def _restore_color_management(self, scene):
        vs, ds = scene.view_settings, scene.display_settings
        cm = self._cm
        for obj, attr in ((ds, 'display_device'), (vs, 'view_transform'), (vs, 'look')):
            try:
                setattr(obj, attr, cm[attr])
            except TypeError:
                pass
        vs.exposure = cm['exposure']
        vs.gamma = cm['gamma']

    def _reroute_materials(self, obj):
        # (node_tree, surface socket name, original from_socket or None, temp node or None)
        self._reroutes = []
        if self.all_slots:
            slots = list(obj.material_slots)
        elif 0 <= obj.active_material_index < len(obj.material_slots):
            slots = [obj.material_slots[obj.active_material_index]]
        else:
            slots = []
        seen = set()
        for slot in slots:
            mat = slot.material if slot else None
            if mat is None or not mat.use_nodes or mat.node_tree is None or mat in seen:
                continue
            seen.add(mat)
            tree = mat.node_tree
            output = tree.get_output_node('ALL')
            if output is None:
                continue
            surface = output.inputs.get('Surface')
            if surface is None or not surface.is_linked:
                continue
            link = surface.links[0]
            shader_node, original_socket = link.from_node, link.from_socket
            color_in = shader_node.inputs.get('Color')
            if color_in is None:
                continue

            temp = None
            if color_in.is_linked:
                source = color_in.links[0].from_socket
            else:
                temp = tree.nodes.new('ShaderNodeRGB')
                temp.outputs[0].default_value = tuple(color_in.default_value)
                source = temp.outputs[0]

            tree.links.remove(link)
            tree.links.new(source, surface)
            self._reroutes.append((tree, surface, original_socket, temp))

    def _restore_materials(self):
        for tree, surface, original_socket, temp in self._reroutes:
            try:
                for l in list(surface.links):
                    tree.links.remove(l)
                tree.links.new(original_socket, surface)
                if temp is not None:
                    tree.nodes.remove(temp)
            except (ReferenceError, RuntimeError):
                pass
        self._reroutes = []

    def _cleanup(self, context):
        if self._draw_handler is not None:
            bpy.types.SpaceView3D.draw_handler_remove(self._draw_handler, 'WINDOW')
            self._draw_handler = None
        context.window.cursor_modal_restore()
        self._restore_materials()
        self._restore_color_management(context.scene)
        context.area.tag_redraw()

    def _on_draw(self):
        self._drawn = True
        if self._color is None:
            return
        size = 60
        x, y = self._mouse_region
        x0, y0 = x + 20, y - 20 - size
        verts = ((x0, y0), (x0 + size, y0), (x0, y0 + size), (x0 + size, y0 + size))
        shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        shader.uniform_float("color", (*self._color, 1.0))
        batch_for_shader(shader, 'TRI_STRIP', {"pos": verts}).draw(shader)

    def _sample_pixel(self, event):
        fb = gpu.state.active_framebuffer_get()
        min_x, min_y, max_x, max_y = fb.viewport_get()
        # Clamping is required for Vulkan.
        x = min(max(event.mouse_x, min_x), max_x - 1)
        y = min(max(event.mouse_y, min_y), max_y - 1)
        try:
            buf = fb.read_color(x, y, 1, 1, 3, 0, 'FLOAT')
        except ValueError:
            return None
        return tuple(buf.to_list()[0][0])

    def _set_brush_color(self, context, color):
        ts = context.tool_settings
        paint = ts.image_paint if context.mode == 'PAINT_TEXTURE' else ts.vertex_paint
        # Blender 5.0 moved unified settings from ToolSettings to Paint.
        ups = getattr(ts, 'unified_paint_settings', None) or getattr(paint, 'unified_paint_settings', None)
        if ups is not None and ups.use_unified_color:
            target = ups
        elif paint.brush is not None:
            target = paint.brush
        else:
            return
        # The framebuffer is sRGB-encoded; linear-subtype brush colors (5.0+) need decoding.
        if target.bl_rna.properties['color'].subtype != 'COLOR_GAMMA':
            color = tuple(_srgb_to_linear(c) for c in color)
        target.color = color

    def invoke(self, context, event):
        scene = context.scene
        self._store_color_management(scene)
        self._set_neutral_color_management(scene)
        self._reroutes = []
        self._drawn = False
        self._color = None
        self._mouse_region = (event.mouse_region_x, event.mouse_region_y)
        if context.object is not None:
            self._reroute_materials(context.object)

        self._draw_handler = bpy.types.SpaceView3D.draw_handler_add(self._on_draw, (), 'WINDOW', 'POST_PIXEL')
        context.window.cursor_modal_set('EYEDROPPER')
        context.window_manager.modal_handler_add(self)
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if event.type in {'ESC', 'RIGHTMOUSE'}:
            self._cleanup(context)
            return {'CANCELLED'}

        if event.type == 'MOUSEMOVE':
            self._mouse_region = (event.mouse_region_x, event.mouse_region_y)
            # Wait until the viewport has redrawn with the neutral setup.
            if self._drawn:
                self._color = self._sample_pixel(event) or self._color
            context.area.tag_redraw()

        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            if not self._drawn:
                context.area.tag_redraw()
                return {'RUNNING_MODAL'}
            try:
                color = self._sample_pixel(event) or self._color
                if color is not None:
                    self._set_brush_color(context, color)
            except Exception as e:
                self.report({'ERROR'}, f"Color pick failed: {e}")
                return {'CANCELLED'}
            finally:
                self._cleanup(context)
            return {'FINISHED'}

        return {'RUNNING_MODAL'}


classes = (PAINT_OT_lr_screen_color_picker,)
