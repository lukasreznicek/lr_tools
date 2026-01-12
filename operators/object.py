import bpy,bmesh
from bpy.props import BoolProperty
from math import degrees
class OBJECT_OT_lr_origin_to_selection(bpy.types.Operator):
    bl_idname = "object.lr_origin_to_selection"
    bl_label = "Origin to Selection"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        cursor = context.scene.cursor
        stored_cursor_location = cursor.location.copy()

        active_object = context.active_object
        
        if active_object.mode == 'OBJECT':
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.view3d.snap_cursor_to_selected()
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')


        elif active_object.mode == 'EDIT':
            bpy.ops.view3d.snap_cursor_to_selected()
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
            bpy.ops.object.mode_set(mode='EDIT')

        cursor.location = stored_cursor_location

        self.report({'INFO'}, 'Origin set.')
        return {'FINISHED'}
    

def flatten(obj, depsgraph=None):
    if not depsgraph:
        depsgraph = bpy.context.evaluated_depsgraph_get()

    oldmesh = obj.data
    obj.data = bpy.data.meshes.new_from_object(obj.evaluated_get(depsgraph))
    obj.modifiers.clear()

    bpy.data.meshes.remove(oldmesh, do_unlink=True)

def unhide_deselect(mesh):
    polygons = len(mesh.polygons)
    edges = len(mesh.edges)
    vertices = len(mesh.vertices)

    mesh.polygons.foreach_set('hide', [False] * polygons)
    mesh.edges.foreach_set('hide', [False] * edges)
    mesh.vertices.foreach_set('hide', [False] * vertices)

    mesh.polygons.foreach_set('select', [False] * polygons)
    mesh.edges.foreach_set('select', [False] * edges)
    mesh.vertices.foreach_set('select', [False] * vertices)
    mesh.update()

def popup_message(message, title="Info", icon="INFO", terminal=True):
    def draw_message(self, context):
        if isinstance(message, list):
            for m in message:
                self.layout.label(text=m)
        else:
            self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw_message, title=title, icon=icon)

    if terminal:
        if icon == "FILE_TICK":
            icon = "ENABLE"
        elif icon == "CANCEL":
            icon = "DISABLE"
        print(icon, title)

        if isinstance(message, list):
            print(" »", ", ".join(message))
        else:
            print(" »", message)

def join(target, objects, select=[]):
    mxi = target.matrix_world.inverted_safe()

    bm = bmesh.new()
    bm.from_mesh(target.data)
    bm.normal_update()
    bm.verts.ensure_lookup_table()

    select_layer = bm.faces.layers.int.get('Machin3FaceSelect')

    if not select_layer:
        select_layer = bm.faces.layers.int.new('Machin3FaceSelect')

    for idx, obj in enumerate(objects):
        mesh = obj.data
        mx = obj.matrix_world
        mesh.transform(mxi @ mx)

        bmm = bmesh.new()
        bmm.from_mesh(mesh)
        bmm.normal_update()
        bmm.verts.ensure_lookup_table()

        obj_select_layer = bmm.faces.layers.int.get('Machin3FaceSelect')

        if not obj_select_layer:
            obj_select_layer = bmm.faces.layers.int.new('Machin3FaceSelect')

        for f in bmm.faces:
            f[obj_select_layer] = idx + 1

        bmm.to_mesh(mesh)
        bmm.free()

        bm.from_mesh(mesh)

        bpy.data.meshes.remove(mesh, do_unlink=True)

    if select:
        for f in bm.faces:
            if f[select_layer] in select:
                f.select_set(True)

    bm.to_mesh(target.data)
    bm.free()

class OBJECT_OT_lr_MeshCut(bpy.types.Operator):
    bl_idname = "object.mesh_cut"
    bl_label = "LR: Mesh Cut"
    bl_description = "Cut a Mesh Object, using another Object.\nALT: Flatten Target Object's Modifier Stack\nSHIFT: Mark Seams"
    bl_options = {'REGISTER', 'UNDO'}

    flatten_target: BoolProperty(name="Flatte Target's Modifier Stack", default=False)
    mark_seams: BoolProperty(name="Mark Seams", default=False)
    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT':
            return context.active_object and context.active_object.type == 'MESH'

    def draw(self, context):
        layout = self.layout
        column = layout.column()

        row = column.row(align=True)
        row.prop(self, 'flatten_target', text="Flatten Target", toggle=True)
        row.prop(self, 'mark_seams', toggle=True)

    def invoke(self, context, event):
        self.flatten_target = event.alt
        self.mark_seams = event.shift
        return self.execute(context)

    def execute(self, context):
        target = context.active_object
        cutters = [obj for obj in context.selected_objects if obj != target]

        if cutters:
            cutter = cutters[0]

            unhide_deselect(target.data)
            unhide_deselect(cutter.data)

            dg = context.evaluated_depsgraph_get()

            flatten(cutter, dg)

            if self.flatten_target:
                flatten(target, dg)

            cutter.data.materials.clear()

            join(target, [cutter], select=[1])

            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.intersect(separate_mode='ALL')
            bpy.ops.object.mode_set(mode='OBJECT')

            bm = bmesh.new()
            bm.from_mesh(target.data)
            bm.normal_update()
            bm.verts.ensure_lookup_table()

            select_layer = bm.faces.layers.int.get('Machin3FaceSelect')
            meshcut_layer = bm.edges.layers.int.get('Machin3EdgeMeshCut')

            if not meshcut_layer:
                meshcut_layer = bm.edges.layers.int.new('Machin3EdgeMeshCut')

            cutter_faces = [f for f in bm.faces if f[select_layer] > 0]
            bmesh.ops.delete(bm, geom=cutter_faces, context='FACES')

            non_manifold = [e for e in bm.edges if not e.is_manifold]

            verts = set()

            for e in non_manifold:
                e[meshcut_layer] = 1

                if self.mark_seams:
                    e.seam = True

                verts.update(e.verts)

            bmesh.ops.remove_doubles(bm, verts=list({v for e in non_manifold for v in e.verts}), dist=0.0001)

            straight_edged = []

            for v in verts:
                if v.is_valid and len(v.link_edges) == 2:
                    e1 = v.link_edges[0]
                    e2 = v.link_edges[1]

                    vector1 = e1.other_vert(v).co - v.co
                    vector2 = e2.other_vert(v).co - v.co

                    angle = degrees(vector1.angle(vector2))

                    if 179 <= angle <= 181:
                        straight_edged.append(v)

            bmesh.ops.dissolve_verts(bm, verts=straight_edged)

            bm.faces.layers.int.remove(select_layer)

            bm.to_mesh(target.data)
            bm.free()

            return {'FINISHED'}
        else:
            popup_message("Select one object first, then select the object to be cut last!", title="Illegal Sellection")
            return {'CANCELLED'}



class OBJECT_OT_lr_select_children_on_selected_objects(bpy.types.Operator):
    '''Adds all children to selection'''
    bl_idname = "object.lr_select_children_on_selected_objects"
    bl_label = "LR: Goes through objects and selects children"
    def execute(self, context):
        sel_obj = bpy.context.selected_objects

        for obj in sel_obj:
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.select_grouped(extend=True, type='CHILDREN_RECURSIVE')
        return {'FINISHED'}	   

class OBJECT_OT_lr_select_root_parent(bpy.types.Operator):
    bl_idname = "object.lr_select_root_parent"
    bl_label = "LR: Selects absolute parent"
    def execute(self, context):
        sel_obj = bpy.context.selected_objects
        
        bpy.ops.object.select_all(action='DESELECT')

        for obj in sel_obj:
            parent_obj = obj
            while parent_obj != None:
                top_parent = parent_obj
                parent_obj = parent_obj.parent

            top_parent.select_set(True)
            bpy.context.view_layer.objects.active = top_parent

        return {'FINISHED'}	    

class OBJECT_OT_select_bevel_object(bpy.types.Operator):
    """Select the bevel object of the active curve"""
    bl_idname = "object.select_bevel_object"
    bl_label = "LR: Select Bevel Object"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == 'CURVE' and obj.data.bevel_object is not None

    def execute(self, context):
        obj = context.active_object
        bevel_object = obj.data.bevel_object

        # Deselect everything
        bpy.ops.object.select_all(action='DESELECT')

        # Select bevel object
        bevel_object.select_set(True)
        context.view_layer.objects.active = bevel_object

        return {'FINISHED'}