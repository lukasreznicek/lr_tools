import bpy
from bpy.types import Menu
from bpy.types import Operator
# from operators import view3d

        
# Left
# Right
# Bottom
# Top
# Top Left
# Top Right
# Bottom Left
# Bottom Right


# ------------------------------------------------------------------------
# PIE MENU: Shading Ex
# ------------------------------------------------------------------------
class VIEW3D_MT_Shading_Ex(Menu):
    bl_idname = "VIEW3D_MT_Shading_Ex"
    bl_label = "Shading Ex"

    def draw(self, context):
        pie = self.layout.menu_pie()
        shading = context.space_data.shading
        overlay = context.space_data.overlay

        # LEFT: Wireframe
        op = pie.operator("wm.context_set_enum",icon='SHADING_WIRE', text="Wireframe", depress=(shading.type == 'WIREFRAME'))
        op.data_path = "space_data.shading.type"
        op.value = 'WIREFRAME'

        # RIGHT: Solid
        op = pie.operator("wm.context_set_enum", text="Solid", icon="SHADING_SOLID", depress=(shading.type == 'SOLID'))
        op.data_path = "space_data.shading.type"
        op.value = 'SOLID'

        # BOTTOM: Toggle X-Ray
        pie.prop(shading, "show_xray", text="Toggle X-Ray", icon='XRAY')

        # TOP: Toggle Overlays
        overlay_visible = getattr(overlay, "show_overlays", False)
        op = pie.operator("wm.context_toggle", text="Toggle Overlays", icon='OVERLAY', depress=overlay_visible)
        op.data_path = "space_data.overlay.show_overlays"

        # TOP LEFT: Material Preview
        op = pie.operator("wm.context_set_enum", text="Material Preview", icon="MATERIAL", depress=(shading.type == 'MATERIAL'))
        op.data_path = "space_data.shading.type"
        op.value = 'MATERIAL'

        # TOP RIGHT: Rendered
        op = pie.operator("wm.context_set_enum", text="Rendered", icon="SHADING_RENDERED", depress=(shading.type == 'RENDERED'))
        op.data_path = "space_data.shading.type"
        op.value = 'RENDERED'
        
        # BOTTOM LEFT
        # pie.operator("mesh.lr_sculpt_selected", text="Sculpt Selected", icon='SCULPTMODE_HLT')
        col = pie.column()                      # Create sublayout
        box = col.box()                         # Draw a framed box
        box.scale_x = 1                         # Slightly larger
        box.scale_y = 1.3
        # box.alert = True                       # 🔴 Make it red-tinted (Blender’s "alert" state)
        box.operator("mesh.lr_sculpt_selected", text="Sculpt Selected", icon='SCULPTMODE_HLT')
        
        # pie.separator()

        # BOTTOM RIGHT: Wireframe Overlay
        wire_visible = getattr(overlay, "show_wireframes", False)
        op = pie.operator("wm.context_toggle",
            text="Wireframe Overlay",
            icon='MOD_WIREFRAME',
            depress=wire_visible)
        op.data_path = "space_data.overlay.show_wireframes"

        # Bottom Right: Show Wireframe toggle
        pie.prop(shading, "show_wire", text="Show Wireframe", icon='MOD_WIREFRAME')


# >>> bpy.context.window_manager.keyconfigs.addon.keymaps['
#                                                          3D View']
#                                                          3D View Tool: Edit Mesh, Box Carve']
#                                                          3D View Tool: Edit Mesh, Circle Carve']
#                                                          3D View Tool: Edit Mesh, Polyline Carve']
#                                                          3D View Tool: Edit Mesh, Zen UV Transform']
#                                                          3D View Tool: Object, Box Carve']
#                                                          3D View Tool: Object, Circle Carve']
#                                                          3D View Tool: Object, Polyline Carve']
#                                                          Asset Browser Main']
#                                                          Curve']
#                                                          Image']
#                                                          Image Editor Tool: Uv, Zen UV Touch']
#                                                          Image Editor Tool: Uv, Zen UV Transform']
#                                                          Mesh']
#                                                          Node Editor']
#                                                          Object Mode']
#                                                          Pose']
#                                                          Property Editor']
#                                                          Screen']
#                                                          Screen Editing']
#                                                          Sculpt']
#                                                          UV Editor']
#                                                          Window']
# ------------------------------------------------------------------------
# PIE MENU: Select Mode Pie
# ------------------------------------------------------------------------
class VIEW3D_MT_Select_Ops_Pie(Menu):
    bl_idname = "VIEW3D_MT_Select_Mode_Pie"
    bl_label = "Select Mode Pie"

    def draw(self, context):
        pie = self.layout.menu_pie()

        # LEFT: Wireframe
        op = pie.operator("mesh.select_edge_ring_multi", text = "Ring Select")
        # pie.separator()

        # RIGHT: Solid
        # pie.separator()
        op = pie.operator("mesh.select_edge_loop_multi", text = "Loop Select")

        # BOTTOM: Toggle X-Ray
        pie.separator()

        # TOP: Toggle Overlays
        # pie.separator()
        op = pie.operator("mesh.select_all", text="Select All")
        op.action = 'SELECT'


        # TOP LEFT: Material Preview
        pie.operator("mesh.region_to_loop", text="Region Loop")

        # TOP RIGHT: Rendered
        pie.separator()
        
        # BOTTOM LEFT
        pie.separator()

        # BOTTOM RIGHT: Wireframe Overlay
        pie.operator("mesh.faces_select_linked_flat", text="Linked Flat")

#pie.separator()
#bpy.ops.mesh.faces_select_linked_flat()
#bpy.ops.mesh.region_to_loop()

# ------------------------------------------------------------------------
# OPERATOR: New Editor Window
# ------------------------------------------------------------------------
class WM_OT_NewEditorWindow(Operator):
    bl_idname = "wm.new_editor_window"
    bl_label = "New Editor Window"

    editor_type: bpy.props.EnumProperty(
        name="Editor Type",
        description="Choose which editor to open in the new window",
        items=[
            ('VIEW_3D',         "3D View",         "Open a new 3D Viewport"),
            ('IMAGE_EDITOR',    "UV Editor",       "Open a new UV/Image Editor"),
            ('NODE_SHADER',     "Shader Editor",   "Open a new Shader Editor"),
            ('NODE_GEOMETRY',   "Geometry Nodes",  "Open a new Geometry Nodes Editor"),
            ('ASSETS',          "Asset Browser",   "Open a new Asset Browser"),
            ('TEXT_EDITOR',     "Text Editor",     "Open a new Text Editor"),
        ],
        default='VIEW_3D',
    )

    def execute(self, context):
        bpy.ops.wm.window_new()
        new_win = bpy.context.window_manager.windows[-1]

        mapping = {
            'VIEW_3D':       ('VIEW_3D',       'VIEW_3D'),
            'IMAGE_EDITOR':  ('IMAGE_EDITOR',  'UV'),
            'NODE_SHADER':   ('NODE_EDITOR',   'ShaderNodeTree'),
            'NODE_GEOMETRY': ('NODE_EDITOR',   'GeometryNodeTree'),
            'ASSETS':        ('FILE_BROWSER',  'ASSETS'),
            'TEXT_EDITOR':   ('TEXT_EDITOR',   'TEXT_EDITOR'),
        }
        area_type, ui_type = mapping[self.editor_type]

        new_win.screen.areas[0].type = area_type
        new_win.screen.areas[0].ui_type = ui_type

        return {'FINISHED'}


# ------------------------------------------------------------------------
# PIE MENU: WindowsPopUp
# ------------------------------------------------------------------------
class VIEW3D_MT_WindowsPopUp(Menu):
    bl_idname = "VIEW3D_MT_WindowsPopUp"
    bl_label = "WindowsPopUp"

    def draw(self, context):
        pie = self.layout.menu_pie()

        # Left
        op = pie.operator("mesh.mark_seams", text="Select All")
        op.clear = True
        # Right
        op = pie.operator("mesh.mark_seams", text="Select All")
        op.clear = False
        pie.operator("wm.new_editor_window", text="UV Editor", icon='IMAGE').editor_type = 'IMAGE_EDITOR'
        
        # Bottom
        pie.operator("wm.new_editor_window", text="Shader Editor", icon='MATSHADERBALL').editor_type = 'NODE_SHADER'
        # Top
        pie.operator("mesh.region_to_loop", text="Select Boundary Loop", icon='GEOMETRY_NODES').editor_type = 'NODE_GEOMETRY'
        
        # Top Left
        op = pie.operator("mesh.mark_sharp", text="Unmark Sharp", icon='ASSET_MANAGER').editor_type = 'ASSETS'
        op.clear = True

        # Top Right
        op = pie.operator("mesh.mark_sharp", text="Unmark Sharp", icon='ASSET_MANAGER').editor_type = 'ASSETS'
        op.clear = False

        # Bottom Left
        pie.separator()
        # Bottom Right
        pie.separator()
    
# ------------------------------------------------------------------------
# PIE MENU: Edge Operators
# ------------------------------------------------------------------------
class VIEW3D_MT_WindowsPopUp(Menu):
    bl_idname = "VIEW3D_MT_WindowsPopUp"
    bl_label = "WindowsPopUp"

    def draw(self, context):
        pie = self.layout.menu_pie()

        # Left
        pie.operator("wm.new_editor_window", text="3D View", icon='VIEW3D').editor_type = 'VIEW_3D'
        # Right
        pie.operator("wm.new_editor_window", text="UV Editor", icon='IMAGE').editor_type = 'IMAGE_EDITOR'
        # Bottom
        pie.operator("wm.new_editor_window", text="Shader Editor", icon='MATSHADERBALL').editor_type = 'NODE_SHADER'
        # Top
        pie.operator("wm.new_editor_window", text="Geometry Nodes", icon='GEOMETRY_NODES').editor_type = 'NODE_GEOMETRY'
        # Top Left
        pie.operator("wm.new_editor_window", text="Asset Browser", icon='ASSET_MANAGER').editor_type = 'ASSETS'
        # Top Right
        pie.operator("wm.new_editor_window", text="Text Editor", icon='FILE_TEXT').editor_type = 'TEXT_EDITOR'
        # Bottom Left
        pie.separator()
        # Bottom Right
        pie.operator("screen.area_join", text="Area Join", icon='AREA_DOCK')
    

# ------------------------------------------------------------------------
# PIE MENU: 3D Cursor
# ------------------------------------------------------------------------
class VIEW3D_MT_3DCursor(Menu):
    bl_idname = "VIEW3D_MT_3DCursor"
    bl_label = "3D Cursor"

    def draw(self, context):
        pie = self.layout.menu_pie()

        # Left
        pie.separator()

        # Right
        pie.separator()

        # Bottom
        # pie.separator()
        pie.operator("view3d.lr_snap_cursor_to_active", text="Snap Cursor to Active", icon='CURSOR')

        # Top
        op = pie.operator("view3d.snap_selected_to_cursor", text="Snap Selected to Cursor", icon='CURSOR')
        op.use_offset = False

        # Top Left
        pie.separator()

        # Top Right
        pie.separator()

        # Bottom Left
        pie.separator()

        # Bottom Right
        pie.separator()
    


# ------------------------------------------------------------------------
# PIE MENU: Save Pie
# ------------------------------------------------------------------------
'''
bpy.ops.export_scene.fbx(
filepath="", 
check_existing=True, 
filter_glob="*.fbx", 
use_selection=False, 
use_visible=False, 
use_active_collection=False, 
collection="", 
global_scale=1, 
apply_unit_scale=True, 
apply_scale_options='FBX_SCALE_NONE', 
use_space_transform=True, 
bake_space_transform=False, 
object_types={'EMPTY', 'CAMERA', 'LIGHT', 'ARMATURE', 'MESH', 'OTHER'}, 
use_mesh_modifiers=True, u
se_mesh_modifiers_render=True, 
mesh_smooth_type='OFF', 
colors_type='SRGB', 
prioritize_active_color=False, 
use_subsurf=False, 
use_mesh_edges=False, 
use_tspace=False, 
use_triangles=False, 
use_custom_props=False, 
add_leaf_bones=True, 
primary_bone_axis='Y', 
secondary_bone_axis='X', 
use_armature_deform_only=False, 
armature_nodetype='NULL', 
bake_anim=True, 
bake_anim_use_all_bones=True, 
bake_anim_use_nla_strips=True, 
bake_anim_use_all_actions=True, 
bake_anim_force_startend_keying=True, 
bake_anim_step=1, 
bake_anim_simplify_factor=1, 
path_mode='AUTO', 
embed_textures=False, 
batch_mode='OFF', 
use_batch_own_dir=True, 
use_metadata=True, 
axis_forward='-Z', 
axis_up='Y')
'''

class VIEW3D_MT_LRPieSave(Menu):
    bl_idname = "VIEW3D_MT_LRPieSave"
    bl_label = "Save Menu"

    def draw(self, context):
        pie = self.layout.menu_pie()
        
        # Left
        pie.operator("wm.open_mainfile", text="Open", icon='FILE_FOLDER')
        # Right
        pie.operator("wm.save_mainfile", text="Save", icon='FILE_TICK')
        # Bottom
        pie.operator("wm.save_as_mainfile", text="Save As...", icon='FILE_TICK')

        # Top: three columns with background
        top_slot = pie.column()
        box = top_slot.box()  # <-- adds a shaded background
        row = box.row()
        
        # Column 1: format names
        col1 = row.column()
        col1.label(text="OBJ")
        col1.label(text="FBX")
        
        # Column 2: import buttons
        col2 = row.column()
        col2.operator("wm.obj_import", text="Import", icon='IMPORT')
        col2.operator("wm.fbx_import", text="Import", icon='IMPORT')
        
        # Column 3: export buttons
        col3 = row.column()
        col3.operator("wm.obj_export", text="Export", icon='EXPORT')
        op = col3.operator("export_scene.fbx", text="Export", icon='EXPORT')
        op.use_selection = True
        op.add_leaf_bones = False

        # Top Left
        pie.separator()
        # Top Right
        pie.separator()
        # Bottom Left
        pie.operator("wm.read_homefile", text="New File", icon='FILE_NEW')
        # pie.separator()
        
        # Bottom Right
        if "lr_exporter_export" in dir(bpy.ops.object):
            op = pie.operator("object.lr_exporter_export", text="Exporter", icon='EXPORT')
            op.export_hidden=True
        else:
            pie.separator()



# import bpy
# from bpy.types import Menu

# # ------------------------------------------------------------------------
# # CONFIGURATION
# # ------------------------------------------------------------------------
# CLASS_BASE_NAME = "Shading Ex"  # <-- Only this menu and operators
# KEY_TYPE = 'Z'
# SHIFT = False
# CTRL = False
# ALT = False

# # ------------------------------------------------------------------------
# # DYNAMIC CLASS CREATION
# # ------------------------------------------------------------------------
# MENU_IDNAME = "VIEW3D_MT_" + CLASS_BASE_NAME.replace(" ", "_")
# MENU_LABEL = CLASS_BASE_NAME

# # Draw function for the pie menu
# def pie_draw(self, context):
#     pie = self.layout.menu_pie()
#     shading = context.space_data.shading
#     overlay = context.space_data.overlay

#     # LEFT: Wireframe
#     op = pie.operator("wm.context_set_enum",
#         icon='SHADING_WIRE',
#         text="Wireframe",
#         depress=(shading.type == 'WIREFRAME'))
#     op.data_path = "space_data.shading.type"
#     op.value = 'WIREFRAME'
#     # RIGHT: Solid
#     op = pie.operator("wm.context_set_enum",
#         text="Solid",
#         icon="SHADING_SOLID",
#         depress=(shading.type == 'SOLID'))
#     op.data_path = "space_data.shading.type"
#     op.value = 'SOLID'
    
    
    
#     # BOTTOM: Toggle X-Ray
#     pie.prop(shading, "show_xray", text="Toggle X-Ray", icon='XRAY')

#     # TOP: Toggle Overlays
#     overlay_visible = getattr(overlay, "show_overlays", False)
#     op = pie.operator("wm.context_toggle",
#         text="Toggle Overlays",
#         icon='OVERLAY',
#         depress=overlay_visible)
#     op.data_path = "space_data.overlay.show_overlays"

#     # TOP LEFT: Material Preview
#     op = pie.operator("wm.context_set_enum",
#         text="Material Preview",
#         icon="MATERIAL",
#         depress=(shading.type == 'MATERIAL'))
#     op.data_path = "space_data.shading.type"
#     op.value = 'MATERIAL'
    
#     # TOP RIGHT: Rendered
#     op = pie.operator("wm.context_set_enum",
#         text="Rendered",
#         icon="SHADING_RENDERED",
#         depress=(shading.type == 'RENDERED'))
#     op.data_path = "space_data.shading.type"
#     op.value = 'RENDERED'
#     # BOTTOM LEFT
#     pie.separator()

#     # BOTTOM RIGHT: Wireframe Overlay
#     wire_visible = getattr(overlay, "show_wireframes", False)
#     op = pie.operator("wm.context_toggle",
#         text="Wireframe Overlay",
#         icon='MOD_WIREFRAME',
#         depress=wire_visible)
#     op.data_path = "space_data.overlay.show_wireframes"

#     # Bottom Right: Show Wireframe toggle
#     pie.prop(shading, "show_wire", text="Show Wireframe", icon='MOD_WIREFRAME')


# # Create the dynamic class
# DynamicPieClass = type(
#     MENU_IDNAME,
#     (Menu,),
#     {
#         "bl_idname": MENU_IDNAME,
#         "bl_label": MENU_LABEL,
#         "draw": pie_draw
#     }
# )

# # ------------------------------------------------------------------------
# # REGISTRATION
# # ------------------------------------------------------------------------
# def register():
#     bpy.utils.register_class(DynamicPieClass)

#     wm = bpy.context.window_manager
#     kc = wm.keyconfigs.addon
#     if not kc:
#         return

#     # Dynamic property name for storing keymaps
#     prop_name = CLASS_BASE_NAME.lower().replace(" ", "_")

#     # Ensure the persistent list exists
#     if not hasattr(bpy.types.WindowManager, prop_name):
#         setattr(bpy.types.WindowManager, prop_name, [])

#     keymap_list = getattr(bpy.types.WindowManager, prop_name)

#     # Remove previous keymaps to prevent duplicates
#     for km, kmi in keymap_list:
#         km.keymap_items.remove(kmi)
#     keymap_list.clear()

#     # Create new keymap
#     km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
#     kmi = km.keymap_items.new(
#         "wm.call_menu_pie",
#         type=KEY_TYPE,
#         value='PRESS',
#         shift=SHIFT,
#         ctrl=CTRL,
#         alt=ALT
#     )
#     kmi.properties.name = DynamicPieClass.bl_idname

#     keymap_list.append((km, kmi))


# def unregister():
#     # Remove keymaps
#     prop_name = CLASS_BASE_NAME.lower().replace(" ", "_")
#     if hasattr(bpy.types.WindowManager, prop_name):
#         keymap_list = getattr(bpy.types.WindowManager, prop_name)
#         for km, kmi in keymap_list:
#             km.keymap_items.remove(kmi)
#         keymap_list.clear()

#     bpy.utils.unregister_class(DynamicPieClass)


# # Safe run in Text Editor
# if __name__ == "__main__":
#     try:
#         unregister()
#     except:
#         pass
#     register()




# import bpy
# from bpy.types import Menu, Operator


# class WM_OT_NewEditorWindow(Operator):
#     bl_idname = "wm.new_editor_window"
#     bl_label = "New Editor Window"
    
#     editor_type: bpy.props.EnumProperty(
#         name="Editor Type",
#         description="Choose which editor to open in the new window",
#         items=[
#             ('VIEW_3D',         "3D View",         "Open a new 3D Viewport"),
#             ('IMAGE_EDITOR',    "UV Editor",       "Open a new UV/Image Editor"),
#             ('NODE_SHADER',     "Shader Editor",   "Open a new Shader Editor"),
#             ('NODE_GEOMETRY',   "Geometry Nodes",  "Open a new Geometry Nodes Editor"),
#             ('ASSETS',          "Asset Browser",   "Open a new Asset Browser"),
#             ('TEXT_EDITOR',     "Text Editor",     "Open a new Text Editor"),
#         ],
#         default='VIEW_3D',
#     )

#     def execute(self, context):
#         # 1) Open a new window
#         bpy.ops.wm.window_new()
#         new_win = bpy.context.window_manager.windows[-1]

#         # 2) Map our enum to Blender area types + ui_types
#         mapping = {
#             'VIEW_3D':       ('VIEW_3D',       'VIEW_3D'),
#             'IMAGE_EDITOR':  ('IMAGE_EDITOR',  'UV'),
#             'NODE_SHADER':   ('NODE_EDITOR',   'ShaderNodeTree'),
#             'NODE_GEOMETRY': ('NODE_EDITOR',   'GeometryNodeTree'),
#             'ASSETS':        ('FILE_BROWSER',  'ASSETS'),
#             'TEXT_EDITOR':   ('TEXT_EDITOR',   'TEXT_EDITOR'),
#         }
#         area_type, ui_type = mapping[self.editor_type]

#         # 3) Find a suitable area in the new window and switch it
#         new_win.screen.areas[0].type = area_type
#         new_win.screen.areas[0].ui_type = ui_type

#         return {'FINISHED'}
    

# # ------------------------------------------------------------------------
# # CONFIGURATION
# # ------------------------------------------------------------------------
# CLASS_BASE_NAME = "WindowsPopUp"  # <-- Only this menu and operators
# KEY_TYPE = 'W'
# SHIFT = True
# CTRL = False
# ALT = False

# # ------------------------------------------------------------------------
# # DYNAMIC CLASS CREATION
# # ------------------------------------------------------------------------
# MENU_IDNAME = "VIEW3D_MT_" + CLASS_BASE_NAME.replace(" ", "_")
# MENU_LABEL = CLASS_BASE_NAME

# # Draw function for the pie menu
# def draw(self, context):
#     pie = self.layout.menu_pie()

#     pie.operator("wm.new_editor_window", text="3D View", icon='VIEW3D').editor_type = 'VIEW_3D'
#     pie.operator("wm.new_editor_window", text="UV Editor", icon='IMAGE').editor_type = 'IMAGE_EDITOR'
#     pie.operator("wm.new_editor_window", text="Shader Editor", icon='MATSHADERBALL').editor_type = 'NODE_SHADER'
#     pie.operator("wm.new_editor_window", text="Geometry Nodes", icon='GEOMETRY_NODES').editor_type = 'NODE_GEOMETRY'
#     pie.operator("wm.new_editor_window", text="Asset Browser", icon='ASSET_MANAGER').editor_type = 'ASSETS'
#     pie.operator("wm.new_editor_window", text="Text Editor", icon='FILE_TEXT').editor_type = 'TEXT_EDITOR'




# # Create the dynamic class
# DynamicPieClass = type(
#     MENU_IDNAME,
#     (Menu,),
#     {
#         "bl_idname": MENU_IDNAME,
#         "bl_label": MENU_LABEL,
#         "draw": draw
#     }
# )

# # ------------------------------------------------------------------------
# # REGISTRATION
# # ------------------------------------------------------------------------
# def register():
#     bpy.utils.register_class(WM_OT_NewEditorWindow)
    
    
#     bpy.utils.register_class(DynamicPieClass)

#     wm = bpy.context.window_manager
#     kc = wm.keyconfigs.addon
#     if not kc:
#         return

#     # Dynamic property name for storing keymaps
#     prop_name = CLASS_BASE_NAME.lower().replace(" ", "_")

#     # Ensure the persistent list exists
#     if not hasattr(bpy.types.WindowManager, prop_name):
#         setattr(bpy.types.WindowManager, prop_name, [])

#     keymap_list = getattr(bpy.types.WindowManager, prop_name)

#     # Remove previous keymaps to prevent duplicates
#     for km, kmi in keymap_list:
#         km.keymap_items.remove(kmi)
#     keymap_list.clear()

#     # Create new keymap
#     km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
#     kmi = km.keymap_items.new(
#         "wm.call_menu_pie",
#         type=KEY_TYPE,
#         value='PRESS',
#         shift=SHIFT,
#         ctrl=CTRL,
#         alt=ALT
#     )
#     kmi.properties.name = DynamicPieClass.bl_idname

#     keymap_list.append((km, kmi))


# def unregister():
#     bpy.utils.unregister_class(WM_OT_NewEditorWindow)
#     # Remove keymaps
#     prop_name = CLASS_BASE_NAME.lower().replace(" ", "_")
#     if hasattr(bpy.types.WindowManager, prop_name):
#         keymap_list = getattr(bpy.types.WindowManager, prop_name)
#         for km, kmi in keymap_list:
#             km.keymap_items.remove(kmi)
#         keymap_list.clear()

#     bpy.utils.unregister_class(DynamicPieClass)


# ========================================================================
# Recreated from Pie Menu Editor
# ========================================================================

# ------------------------------------------------------------------------
# OPERATORS
# ------------------------------------------------------------------------
class LR_OT_PieSnapPreset(Operator):
    bl_idname = "lr.pie_snap_preset"
    bl_label = "Snap Preset"
    bl_options = {'REGISTER', 'UNDO'}

    preset: bpy.props.EnumProperty(
        items=[
            ('NORMAL', "Normal", ""),
            ('GRID_ABS', "Grid Abs", ""),
            ('GRID_REL', "Grid Rel", ""),
            ('VERTEX', "Vertex", ""),
            ('FACE', "Face", ""),
            ('RETOPO', "Retopology", ""),
        ],
        default='VERTEX',
    )

    def execute(self, context):
        ts = context.scene.tool_settings
        # Only the retopology preset turns snapping on; all others turn it off
        ts.use_snap = (self.preset == 'RETOPO')
        if self.preset == 'RETOPO':
            try:
                ts.snap_elements = {'FACE', 'FACE_NEAREST'}
            except TypeError:
                ts.snap_elements = {'FACE_PROJECT', 'FACE_NEAREST'}
            ts.snap_target = 'ACTIVE'
            ts.use_snap_align_rotation = False
        elif self.preset in {'NORMAL', 'FACE'}:
            ts.snap_elements = {'FACE'}
            ts.snap_target = 'ACTIVE'
            ts.use_snap_align_rotation = (self.preset == 'NORMAL')
        elif self.preset == 'VERTEX':
            ts.snap_elements = {'VERTEX'}
            ts.snap_target = 'ACTIVE'
            ts.use_snap_align_rotation = False
        else:
            ts.snap_elements = {'INCREMENT'}
            ts.use_snap_grid_absolute = (self.preset == 'GRID_ABS')
        return {'FINISHED'}


class LR_OT_PieViewSelectedObjectMode(Operator):
    bl_idname = "lr.pie_view_selected_object_mode"
    bl_label = "View Selected in Object Mode"
    bl_description = "Switch to object mode, frame the selection and return to edit mode"

    def execute(self, context):
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.view3d.view_selected(use_all_regions=False)
        bpy.ops.object.mode_set(mode='EDIT')
        return {'FINISHED'}


class LR_OT_PieTexelDensity(Operator):
    bl_idname = "lr.pie_texel_density_10_24"
    bl_label = "Set 10.24 on 2k"
    bl_description = "Set texel density 10.24 for a 2048 texture (Texel Density Checker addon)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if not hasattr(bpy.ops.object, "texel_density_preset_set"):
            self.report({'WARNING'}, "Texel Density Checker addon is not enabled")
            return {'CANCELLED'}
        context.scene.td.texture_size = "2048"
        bpy.ops.object.texel_density_preset_set(td_value="10.24")
        return {'FINISHED'}


class LR_OT_PieZenFitToTrim(Operator):
    bl_idname = "lr.pie_zenuv_fit_to_trim"
    bl_label = "Set Active Trim and Fit"
    bl_description = "Pick the trim under the mouse and fit selection to it (Zen UV addon)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if not hasattr(bpy.ops.uv, "zenuv_fit_to_trim"):
            self.report({'WARNING'}, "Zen UV addon is not enabled")
            return {'CANCELLED'}
        bpy.ops.uv.zenuv_set_active_trim_mouseover('INVOKE_DEFAULT')
        bpy.ops.uv.zenuv_fit_to_trim(
            op_align_to='lc', op_order='ONE_BY_ONE', fit_mode='TO_TRIM_T',
            op_fit_axis='V', op_padding=0.0)
        return {'FINISHED'}


class LR_OT_PieZenTrimOverlay(Operator):
    bl_idname = "lr.pie_zenuv_trim_overlay"
    bl_label = "Trim Overlay"
    bl_description = "Show trims in the UV editor (Zen UV addon)"

    def execute(self, context):
        try:
            context.scene.zen_uv.ui.uv_tool.display_trims = True
        except AttributeError:
            self.report({'WARNING'}, "Zen UV addon is not enabled")
            return {'CANCELLED'}
        return {'FINISHED'}


class LR_OT_PieWireOverlay(Operator):
    bl_idname = "lr.pie_wire_overlay"
    bl_label = "Set Wireframe Overlay"

    state: bpy.props.BoolProperty(default=True)

    def execute(self, context):
        context.space_data.overlay.show_wireframes = self.state
        return {'FINISHED'}


# ------------------------------------------------------------------------
# POPUP MENUS (used by the pies below)
# ------------------------------------------------------------------------
class VIEW3D_MT_LRPopupMerge(Menu):
    bl_idname = "VIEW3D_MT_LRPopupMerge"
    bl_label = "Merge"

    def draw(self, context):
        layout = self.layout
        layout.operator("mesh.merge", text="Collapse").type = 'COLLAPSE'
        layout.operator("mesh.remove_doubles", text="Merge: Distance")


class VIEW3D_MT_LRPopupMeshUtils(Menu):
    bl_idname = "VIEW3D_MT_LRPopupMeshUtils"
    bl_label = "Mesh Utils"

    def draw(self, context):
        layout = self.layout
        ts = context.scene.tool_settings
        layout.prop(ts, "use_transform_correct_face_attributes", text="UV Preserve", icon='TEXTURE_DATA', toggle=True)
        layout.prop(ts, "use_mesh_automerge", text="Automerge", icon='AUTOMERGE_OFF', toggle=True)


class VIEW3D_MT_LRPopupExport(Menu):
    bl_idname = "VIEW3D_MT_LRPopupExport"
    bl_label = "Export"

    def draw(self, context):
        layout = self.layout
        layout.operator("autoreload.reload", text="Reload Images", icon='FILE_REFRESH').behavior = 'images'
        layout.separator()
        op = layout.operator("object.lr_exporter_export", text="Export Selected", icon='EXPORT')
        op.export_hidden = True
        op = layout.operator("object.lr_exporter_export", text="Export for mask", icon='EXPORT')
        op.export_for_mask = True


class VIEW3D_MT_LRPopupObjectConversion(Menu):
    bl_idname = "VIEW3D_MT_LRPopupObjectConversion"
    bl_label = "Object Conversion"

    def draw(self, context):
        layout = self.layout
        layout.operator("object.convert", text="To Mesh").target = 'MESH'
        op = layout.operator("object.make_single_user", text="Single User")
        op.object = True
        op.obdata = True
        op.material = False
        op.animation = False


class VIEW3D_MT_LRPopupHide(Menu):
    bl_idname = "VIEW3D_MT_LRPopupHide"
    bl_label = "Hide"

    def draw(self, context):
        layout = self.layout
        for label, name in (("HP", "_HP"), ("LP", "_LP"), ("UCX", "UCX_"), ("CAGE", "_cage")):
            row = layout.row()
            op = row.operator("object.lr_hide_object", text=label, icon='HIDE_OFF')
            op.name = name
            op.hide = False
            op = row.operator("object.lr_hide_object", text=label, icon='HIDE_ON')
            op.name = name
            op.hide = True
        row = layout.row()
        row.operator("object.lr_hide_wire_object", text="Wire", icon='HIDE_OFF').hide_wire = False
        row.operator("object.lr_hide_wire_object", text="Wire", icon='HIDE_ON').hide_wire = True


# ------------------------------------------------------------------------
# PIE MENU: Mesh Edit
# ------------------------------------------------------------------------
class VIEW3D_MT_LRPieMeshEdit(Menu):
    bl_idname = "VIEW3D_MT_LRPieMeshEdit"
    bl_label = "Mesh Edit"

    def draw(self, context):
        pie = self.layout.menu_pie()
        has_looptools = hasattr(bpy.ops.mesh, "looptools_circle")

        # Left
        if has_looptools:
            op = pie.operator("mesh.looptools_circle", text="Circle", icon='MESH_CIRCLE')
            op.custom_radius = False
            op.fit = 'best'
            op.flatten = True
            op.influence = 100
            op.radius = 1
            op.regular = True
        else:
            pie.separator()
        # Right
        pie.menu("VIEW3D_MT_LRPopupMerge", text="Merge")
        # Bottom
        if has_looptools:
            op = pie.operator("mesh.looptools_space", text="Space")
            op.influence = 100
            op.input = 'selected'
            op.interpolation = 'cubic'
        else:
            pie.separator()
        # Top
        if has_looptools:
            op = pie.operator("mesh.looptools_curve", text="Curve")
            op.boundaries = True
            op.influence = 100
            op.interpolation = 'cubic'
            op.regular = False
            op.restriction = 'none'
        else:
            pie.separator()
        # Top Left
        if has_looptools:
            op = pie.operator("mesh.looptools_flatten", text="Flatten")
            op.influence = 100
            op.plane = 'best_fit'
            op.restriction = 'none'
        else:
            pie.separator()
        # Top Right
        pie.operator("lr.pie_texel_density_10_24", text="Set TD 10.24")
        # Bottom Left
        pie.operator("mesh.subdivide", text="Subdivide", icon='MESH_GRID')
        # Bottom Right
        if hasattr(bpy.ops.mesh, "set_edge_flow"):
            op = pie.operator("mesh.set_edge_flow", text="Set Edge Flow", icon='RNDCURVE')
            op.tension = 180
            op.iterations = 1
        else:
            pie.separator()


# ------------------------------------------------------------------------
# PIE MENU: Curve Edit
# ------------------------------------------------------------------------
class VIEW3D_MT_LRPieCurveEdit(Menu):
    bl_idname = "VIEW3D_MT_LRPieCurveEdit"
    bl_label = "Curve Edit"

    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.separator()                                                 # Left
        pie.operator("curve.select_next", text="Select Next")           # Right
        pie.separator()                                                 # Bottom
        pie.operator("curve.select_linked", text="Select Linked All")   # Top
        pie.separator()                                                 # Top Left
        pie.operator("curve.subdivide", text="Subdivide")               # Top Right
        pie.separator()                                                 # Bottom Left
        pie.operator("curve.select_previous", text="Select Previous")   # Bottom Right


# ------------------------------------------------------------------------
# PIE MENU: Mesh Utils
# ------------------------------------------------------------------------
class VIEW3D_MT_LRPieMeshUtils(Menu):
    bl_idname = "VIEW3D_MT_LRPieMeshUtils"
    bl_label = "Mesh Utils"

    def draw(self, context):
        pie = self.layout.menu_pie()
        # Left
        pie.operator("mesh.mark_seam", text="Unmark Seam", icon='EDGESEL').clear = True
        # Right
        pie.operator("mesh.mark_seam", text="Mark Seam", icon='EDGE_SEAM').clear = False
        # Bottom
        pie.menu("VIEW3D_MT_LRPopupMeshUtils", text="Mesh Utils Menu")
        # Top
        pie.operator("mesh.region_to_loop", text="Select Boundary Loop", icon='SELECT_SET')
        # Top Left
        pie.operator("mesh.mark_sharp", text="Unmark Sharp", icon='SPHERECURVE').clear = True
        # Top Right
        pie.operator("mesh.mark_sharp", text="Mark Sharp", icon='LINCURVE')
        # Bottom Left
        pie.operator("mesh.lr_sculpt_selected", text="Sculpt Selected", icon='SCULPTMODE_HLT')
        # Bottom Right
        pie.operator("mesh.faces_select_linked_flat", text="Select Linked Flat Faces", icon='UV_FACESEL')


# ------------------------------------------------------------------------
# PIE MENU: Object Utils
# ------------------------------------------------------------------------
class VIEW3D_MT_LRPieObjectUtils(Menu):
    bl_idname = "VIEW3D_MT_LRPieObjectUtils"
    bl_label = "Object Utils"

    def draw(self, context):
        pie = self.layout.menu_pie()
        # Left
        pie.prop(context.space_data.overlay, "show_face_orientation", text="Face Orientation", toggle=True)
        # Right
        pie.menu("VIEW3D_MT_LRPopupObjectConversion", text="Make Single User")
        # Bottom
        pie.menu("VIEW3D_MT_LRPopupExport", text="Export")
        # Top
        pie.prop(context.scene.tool_settings, "use_transform_skip_children", text="Transform Parents",
                 icon='OBJECT_ORIGIN', toggle=True)
        # Top Left
        pie.operator("object.modifier_add", text="Weighted Normals", icon='MOD_NORMALEDIT').type = 'WEIGHTED_NORMAL'
        # Top Right
        op = pie.operator("object.transform_apply", text="Apply Transformation inc. instances", icon='FREEZE')
        op.location = False
        op.rotation = True
        op.scale = True
        op.isolate_users = True
        # Bottom Left
        pie.operator("object.lr_select_root_parent", text="Select: Root Parent", icon='SORT_DESC')
        # Bottom Right
        pie.operator("object.lr_select_children_on_selected_objects", text="Select: Add Children", icon='SORT_ASC')


# ------------------------------------------------------------------------
# PIE MENU: Snap Preset
# ------------------------------------------------------------------------
class VIEW3D_MT_LRPieSnapPreset(Menu):
    bl_idname = "VIEW3D_MT_LRPieSnapPreset"
    bl_label = "Snap Preset"

    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator("lr.pie_snap_preset", text="Normal", icon='ORIENTATION_NORMAL').preset = 'NORMAL'      # Left
        pie.operator("lr.pie_snap_preset", text="Grid Abs", icon='SNAP_GRID').preset = 'GRID_ABS'           # Right
        pie.separator()                                                                                      # Bottom
        pie.operator("lr.pie_snap_preset", text="Vertex", icon='SNAP_VERTEX').preset = 'VERTEX'             # Top
        pie.operator("lr.pie_snap_preset", text="Retopology", icon='MOD_MESHDEFORM').preset = 'RETOPO'      # Top Left
        pie.operator("lr.pie_snap_preset", text="Face", icon='SNAP_FACE').preset = 'FACE'                   # Top Right
        pie.separator()                                                                                      # Bottom Left
        pie.operator("lr.pie_snap_preset", text="Grid Rel", icon='SNAP_GRID').preset = 'GRID_REL'           # Bottom Right


# ------------------------------------------------------------------------
# PIE MENU: View Selected / Hide
# ------------------------------------------------------------------------
class VIEW3D_MT_LRPieViewSelected(Menu):
    bl_idname = "VIEW3D_MT_LRPieViewSelected"
    bl_label = "View Selected"

    def draw(self, context):
        pie = self.layout.menu_pie()
        # Left
        pie.operator("lr.pie_wire_overlay", text="Wire Off").state = False
        # Right
        pie.operator("lr.pie_wire_overlay", text="Wire On").state = True
        # Bottom
        pie.menu("VIEW3D_MT_LRPopupHide", text="Hide")
        # Top
        pie.operator("object.lr_unhide_ucx", text="Unhide all UCX objects")
        # Top Left
        pie.operator("object.lr_remove_checker", text="Remove Checker", icon='MESH_PLANE')
        # Top Right
        pie.operator("object.lr_assign_checker", text="Assign Checker", icon='TEXTURE')
        # Bottom Left
        op = pie.operator("object.lr_hide_subd_modifier", text="Hide SubD")
        op.hide_subsurf = True
        op.hide_subsurf_active = False
        # Bottom Right
        op = pie.operator("object.lr_hide_subd_modifier", text="Show SubD")
        op.hide_subsurf = False
        op.hide_subsurf_active = False


# ------------------------------------------------------------------------
# PIE MENU: UV Pie
# ------------------------------------------------------------------------
class IMAGE_MT_LRPieUV(Menu):
    bl_idname = "IMAGE_MT_LRPieUV"
    bl_label = "UV Pie"

    def draw(self, context):
        pie = self.layout.menu_pie()
        # Left
        pie.operator("uv.mark_seam", text="Clear Seam", icon='EDGESEL').clear = True
        # Right
        pie.operator("uv.mark_seam", text="Mark Seam", icon='EDGE_SEAM').clear = False
        # Bottom
        pie.separator()
        # Top
        pie.operator("lr.pie_zenuv_fit_to_trim", text="Set Active Trim", icon='EYEDROPPER')
        # Top Left
        pie.operator("lr.pie_zenuv_trim_overlay", text="Trim Overlay", icon='OVERLAY')
        # Top Right
        pie.operator("lr.pie_texel_density_10_24", text="Set 10.24 on 2k", icon='TEXTURE')
        # Bottom Left
        pie.separator()
        # Bottom Right
        pie.operator("uv.average_islands_scale", text="Average Islands Scale")


# ------------------------------------------------------------------------
# PIE MENU: UV Align
# ------------------------------------------------------------------------
class IMAGE_MT_LRPieUVAlign(Menu):
    bl_idname = "IMAGE_MT_LRPieUVAlign"
    bl_label = "UV Align"

    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.separator()  # Left
        pie.separator()  # Right
        pie.separator()  # Bottom
        pie.separator()  # Top
        pie.operator("uv.lr_snap_to_corner", text="Align TopLeft").corner = 'TOP_LEFT'
        pie.operator("uv.lr_snap_to_corner", text="Align TopRight").corner = 'TOP_RIGHT'
        pie.operator("uv.lr_snap_to_corner", text="Align BottomLeft").corner = 'BOTTOM_LEFT'
        pie.operator("uv.lr_snap_to_corner", text="Align BottomRight").corner = 'BOTTOM_RIGHT'


# ------------------------------------------------------------------------
# PIE MENU: UV Scale
# ------------------------------------------------------------------------
class IMAGE_MT_LRPieUVScale(Menu):
    bl_idname = "IMAGE_MT_LRPieUVScale"
    bl_label = "UV Scale"

    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.separator()  # Left
        pie.separator()  # Right
        pie.separator()  # Bottom
        pie.separator()  # Top
        pie.operator("uv.lr_scale_from_corner", text="Scale TopLeft").corner = 'TOP_LEFT'
        pie.operator("uv.lr_scale_from_corner", text="Scale TopRight").corner = 'TOP_RIGHT'
        pie.operator("uv.lr_scale_from_corner", text="Scale BottomLeft").corner = 'BOTTOM_LEFT'
        pie.operator("uv.lr_scale_from_corner", text="Scale BottomRight").corner = 'BOTTOM_RIGHT'
