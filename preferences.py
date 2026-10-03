import bpy
import rna_keymap_ui
from .keymaps import addon_keymaps


class AddonPreferences(bpy.types.AddonPreferences):
    '''Displays all keymaps created above in settings'''
    bl_idname = __package__

    def draw(self, context):
        # Search for keymap items in the addon's keymap list (addon_keymaps) from within Blender settings and display the menu

        layout = self.layout
        box = layout.box()
        color = box.column()
        color.label(text="Keymap List:",icon="KEYINGSET")

        wm = bpy.context.window_manager
        kc = wm.keyconfigs.user
        old_km_name = ""
        get_kmi_l = []
        for km_add, kmi_add in addon_keymaps:
            for km_con in kc.keymaps:
                if km_add.name == km_con.name:
                    km = km_con
                    break

            for kmi_con in km.keymap_items:
                if kmi_add.idname == kmi_con.idname:
                    if kmi_add.name == kmi_con.name:
                        get_kmi_l.append((km,kmi_con))

        get_kmi_l = sorted(set(get_kmi_l), key=get_kmi_l.index)

        for km, kmi in get_kmi_l:
            if not km.name == old_km_name:
                color.label(text=str(km.name),icon="DOT")
            color.context_pointer_set("keymap", km)
            rna_keymap_ui.draw_kmi([], kc, km, kmi, color, 0)
            color.separator()
            old_km_name = km.name
