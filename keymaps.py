import bpy
from .ui import pie_menus

addon_keymaps = []
def register_keymaps():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:

        # Pie Menu - Snapping Presets
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new(
            "wm.call_menu_pie",
            type='Z',
            value='PRESS',
            shift=False,
            ctrl=False,
            alt=False
        )
        kmi.properties.name = pie_menus.VIEW3D_MT_Shading_Ex.bl_idname
        addon_keymaps.append((km, kmi))

        # Pie Menu - Select
        km = kc.keymaps.get('Mesh')
        if km is None:
            km = kc.keymaps.new(name='Mesh', space_type='VIEW_3D')

        # km = kc.keymaps.new(name='Mesh', space_type='VIEW_3D')
        kmi = km.keymap_items.new(
            "wm.call_menu_pie",
            type='A',
            value='PRESS',
            shift=False,
            ctrl=False,
            alt=False
        )
        kmi.properties.name = pie_menus.VIEW3D_MT_Select_Ops_Pie.bl_idname
        addon_keymaps.append((km, kmi))


        # Pie Menu - LRPieSave
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new(
            "wm.call_menu_pie",
            type='S',
            value='PRESS',
            shift=False,
            ctrl=True,
            alt=False
        )

        kmi.properties.name = pie_menus.VIEW3D_MT_LRPieSave.bl_idname
        addon_keymaps.append((km, kmi))


        # Pie Menu - Origin menu.
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new(
            "wm.call_menu_pie",
            type='S',
            value='PRESS',
            shift=True,
            ctrl=False,
            alt=False
        )
        kmi.properties.name = pie_menus.VIEW3D_MT_3DCursor.bl_idname
        addon_keymaps.append((km, kmi))


        # Pie Menu - Windows PopUp
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new(
            "wm.call_menu_pie",
            type='W',
            value='PRESS',
            shift=False,
            ctrl=False,
            alt=True
        )
        kmi.properties.name = pie_menus.VIEW3D_MT_WindowsPopUp.bl_idname
        addon_keymaps.append((km, kmi))


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
