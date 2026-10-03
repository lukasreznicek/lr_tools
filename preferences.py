import bpy
import rna_keymap_ui
from . import keymaps
from .keymaps import addon_keymaps


def _same_pie(kmi_add, kmi_con):
    # call_menu_pie items must also point to the same menu
    if kmi_add.idname != "wm.call_menu_pie":
        return True
    return kmi_add.properties.name == kmi_con.properties.name


class AddonPreferences(bpy.types.AddonPreferences):
    '''Displays all keymaps created above in settings'''
    bl_idname = __package__

    def draw(self, context):
        layout = self.layout
        wm = bpy.context.window_manager
        kc = wm.keyconfigs.user

        keymap_items = {
            "Pie Menus": [],
            "Operators": [],
        }

        for km_add, kmi_add in addon_keymaps:
            km = None
            for km_con in kc.keymaps:
                if km_add.name == km_con.name:
                    km = km_con
                    break

            if km is None:
                continue

            for kmi_con in km.keymap_items:
                if kmi_add.idname == kmi_con.idname:
                    if kmi_add.name == kmi_con.name and _same_pie(kmi_add, kmi_con):
                        category = (
                            "Pie Menus"
                            if kmi_add.idname == "wm.call_menu_pie"
                            else "Operators"
                        )
                        keymap_items[category].append((km, kmi_con))

        for category in ("Pie Menus", "Operators"):
            box = layout.box()
            column = box.column()
            column.label(text=category, icon="KEYINGSET")

            items = keymap_items[category]
            items = sorted(set(items), key=items.index)
            old_km_name = ""
            for km, kmi in items:
                if km.name != old_km_name:
                    column.label(text=km.name, icon="DOT")
                column.context_pointer_set("keymap", km)
                rna_keymap_ui.draw_kmi([], kc, km, kmi, column, 0)
                column.separator()
                old_km_name = km.name
