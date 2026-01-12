import bpy
from bpy.types import Menu
from bpy.types import Operator

        
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
        op = pie.operator("wm.context_set_enum",
            icon='SHADING_WIRE',
            text="Wireframe",
            depress=(shading.type == 'WIREFRAME'))
        op.data_path = "space_data.shading.type"
        op.value = 'WIREFRAME'
        # RIGHT: Solid
        op = pie.operator("wm.context_set_enum",
            text="Solid",
            icon="SHADING_SOLID",
            depress=(shading.type == 'SOLID'))
        op.data_path = "space_data.shading.type"
        op.value = 'SOLID'

        # BOTTOM: Toggle X-Ray
        pie.prop(shading, "show_xray", text="Toggle X-Ray", icon='XRAY')

        # TOP: Toggle Overlays
        overlay_visible = getattr(overlay, "show_overlays", False)
        op = pie.operator("wm.context_toggle",
            text="Toggle Overlays",
            icon='OVERLAY',
            depress=overlay_visible)
        op.data_path = "space_data.overlay.show_overlays"

        # TOP LEFT: Material Preview
        op = pie.operator("wm.context_set_enum",
            text="Material Preview",
            icon="MATERIAL",
            depress=(shading.type == 'MATERIAL'))
        op.data_path = "space_data.shading.type"
        op.value = 'MATERIAL'

        # TOP RIGHT: Rendered
        op = pie.operator("wm.context_set_enum",
            text="Rendered",
            icon="SHADING_RENDERED",
            depress=(shading.type == 'RENDERED'))
        op.data_path = "space_data.shading.type"
        op.value = 'RENDERED'
        
        # BOTTOM LEFT
        # pie.operator("mesh.lr_sculpt_selected", text="Sculpt Selected", icon='SCULPTMODE_HLT')
        col = pie.column()                     # Create sublayout
        box = col.box()                        # Draw a framed box
        box.scale_x = 1                      # Slightly larger
        box.scale_y = 1.3
        # box.alert = True                       # 🔴 Make it red-tinted (Blender’s "alert" state)
        box.operator("mesh.lr_sculpt_selected",
                     text="Sculpt Selected",  # Add emoji / uppercase to stand out
                     icon='SCULPTMODE_HLT')
        
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
            op.export_for_mask=False
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
