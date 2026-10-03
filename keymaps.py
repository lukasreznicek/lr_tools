import bpy
from .ui import pie_menus

addon_keymaps = []

# (pie id, preference label, keymap name, space type, key, modifiers, operator, properties)
# Modifiers: set of 'shift', 'ctrl', 'alt', 'any'.
_PIE = "wm.call_menu_pie"
PIE_GROUPS = (
    ("shading_ex", "Shading Ex (Z)", "3D View", 'VIEW_3D', 'Z', set(), _PIE, pie_menus.VIEW3D_MT_Shading_Ex.bl_idname),
    ("select_ops", "Select Mode (A, Edit Mesh)", "Mesh", 'EMPTY', 'A', set(), _PIE, pie_menus.VIEW3D_MT_Select_Ops_Pie.bl_idname),
    ("save", "Save (Ctrl+S)", "3D View", 'VIEW_3D', 'S', {'ctrl'}, _PIE, pie_menus.VIEW3D_MT_LRPieSave.bl_idname),
    ("cursor", "3D Cursor (Shift+S)", "3D View", 'VIEW_3D', 'S', {'shift'}, _PIE, pie_menus.VIEW3D_MT_3DCursor.bl_idname),
    ("windows", "Windows PopUp (Alt+W)", "3D View", 'VIEW_3D', 'W', {'alt'}, _PIE, pie_menus.VIEW3D_MT_WindowsPopUp.bl_idname),
    ("mesh_edit", "Mesh Edit (Shift+E, Edit Mesh)", "Mesh", 'EMPTY', 'E', {'shift'}, _PIE, pie_menus.VIEW3D_MT_LRPieMeshEdit.bl_idname),
    ("curve_edit", "Curve Edit (Shift+E, Edit Curve)", "Curve", 'EMPTY', 'E', {'shift'}, _PIE, pie_menus.VIEW3D_MT_LRPieCurveEdit.bl_idname),
    ("mesh_utils", "Mesh Utils (Shift+W, Edit Mesh)", "Mesh", 'EMPTY', 'W', {'shift'}, _PIE, pie_menus.VIEW3D_MT_LRPieMeshUtils.bl_idname),
    ("object_utils", "Object Utils (Shift+W)", "3D View", 'VIEW_3D', 'W', {'shift'}, _PIE, pie_menus.VIEW3D_MT_LRPieObjectUtils.bl_idname),
    ("snap_preset", "Snap Preset (Ctrl+Alt+S)", "3D View", 'VIEW_3D', 'S', {'ctrl', 'alt'}, _PIE, pie_menus.VIEW3D_MT_LRPieSnapPreset.bl_idname),
    ("view_selected", "View Selected / Hide (Ctrl+RMB)", "3D View", 'VIEW_3D', 'RIGHTMOUSE', {'ctrl'}, _PIE, pie_menus.VIEW3D_MT_LRPieViewSelected.bl_idname),
    ("uv_pie", "UV Pie (W, UV Editor)", "UV Editor", 'EMPTY', 'W', {'any'}, _PIE, pie_menus.IMAGE_MT_LRPieUV.bl_idname),
    ("uv_align", "UV Align (Alt+Q, UV Editor)", "UV Editor", 'EMPTY', 'Q', {'alt'}, _PIE, pie_menus.IMAGE_MT_LRPieUVAlign.bl_idname),
    ("uv_scale", "UV Scale (Alt+Z, UV Editor)", "UV Editor", 'EMPTY', 'Z', {'alt'}, _PIE, pie_menus.IMAGE_MT_LRPieUVScale.bl_idname),
    ("sculpt_selected", "Sculpt Selected (Ctrl+Alt+Q)", "3D View", 'VIEW_3D', 'Q', {'ctrl', 'alt'}, "mesh.lr_sculpt_selected", None),
    ("view_all_mesh", "View Selected in Object Mode (Shift+Alt+RMB)", "3D View", 'VIEW_3D', 'RIGHTMOUSE', {'shift', 'alt'}, "lr.pie_view_selected_object_mode", None),
)


def register_pie_keymaps():
    kc = bpy.context.window_manager.keyconfigs.addon
    if not kc:
        return

    for _key, _label, km_name, space, kmi_type, mods, idname, menu_name in PIE_GROUPS:
        km = kc.keymaps.get(km_name) or kc.keymaps.new(name=km_name, space_type=space)
        kmi = km.keymap_items.new(
            idname,
            type=kmi_type,
            value='PRESS',
            shift='shift' in mods,
            ctrl='ctrl' in mods,
            alt='alt' in mods,
            any='any' in mods,
        )
        if menu_name:
            kmi.properties.name = menu_name
        addon_keymaps.append((km, kmi))


def register_keymaps():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:

        register_pie_keymaps()
        # Pie Menu - Multires offset Decrease
        km = kc.keymaps.new(name='Sculpt', space_type= 'EMPTY')
        kmi = km.keymap_items.new('lr.offset_multires_sculpt_subd', type= 'D', value='PRESS', shift=True, ctrl=False, alt=False)
        kmi.properties.decrease = True
        kmi.active = True
        addon_keymaps.append((km, kmi))
        
        # Pie Menu - Multires offset Increase
        km = kc.keymaps.new(name='Sculpt', space_type= 'EMPTY')
        kmi = km.keymap_items.new('lr.offset_multires_sculpt_subd', type= 'D', value='PRESS', shift=False, ctrl=False, alt=False)
        kmi.properties.decrease = False
        kmi.active = True
        addon_keymaps.append((km, kmi))

        # View rotation - Left
        km = kc.keymaps.new(name='3D View', space_type= 'VIEW_3D')
        kmi = km.keymap_items.new('lr.view_object_rotate', type= 'TWO', value='PRESS', shift=True, ctrl=False, alt=False)
        kmi.properties.rotate_left = False
        kmi.active = False
        addon_keymaps.append((km, kmi))

        # View rotation - Right
        km = kc.keymaps.new(name='3D View', space_type= 'VIEW_3D')
        kmi = km.keymap_items.new('lr.view_object_rotate', type= 'ONE', value='PRESS', shift=True, ctrl=False, alt=False)
        kmi.properties.rotate_left = True
        kmi.active = False
        addon_keymaps.append((km, kmi))

        # View rotation - Left - Image Editor
        km = kc.keymaps.new(name='Image', space_type= 'IMAGE_EDITOR')
        kmi = km.keymap_items.new('lr.view_object_rotate', type= 'TWO', value='PRESS', shift=True, ctrl=False, alt=False)
        kmi.properties.rotate_left = False
        kmi.active = False
        addon_keymaps.append((km, kmi))

        # View rotation - Right - Image Editor
        km = kc.keymaps.new(name='Image', space_type= 'IMAGE_EDITOR')
        kmi = km.keymap_items.new('lr.view_object_rotate', type= 'ONE', value='PRESS', shift=True, ctrl=False, alt=False)
        kmi.properties.rotate_left = True
        kmi.active = False
        addon_keymaps.append((km, kmi))

def unregister_keymaps():
    for km,kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

