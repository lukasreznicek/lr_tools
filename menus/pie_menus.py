import bpy
from bpy.types import Menu


class VIEW3D_MT_PIE_snapping_presets(Menu):
    # label is displayed at the center of the pie menu.
    bl_label = "Snapping Presets"





    def draw(self, context):
        layout = self.layout

        pie = layout.menu_pie()
        # operator_enum will just spread all available options
        # for the type enum of the operator on the pie
        pie.operator_enum("mesh.select_mode", "type")
