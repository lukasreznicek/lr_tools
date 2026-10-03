import bpy
from ..operators import object, scene, window


class VIEW3D_MT_LR_Menu(bpy.types.Menu):
    bl_label = "LR Tools"
    bl_idname = "VIEW3D_MT_LR_Menu"

    def draw(self, context):
        layout = self.layout
        pass
        layout.operator("lr.name_high_poly_bake", text="Name High Poly / Low Poly", icon = 'FILE_TEXT')
        layout.operator(object.OBJECT_OT_lr_MeshCut.bl_idname, icon="SCULPTMODE_HLT")

def add_to_object_context_menu(self, context):
    if context.mode == 'OBJECT':
        layout = self.layout
        layout.separator()
        layout.menu("VIEW3D_MT_LR_Menu", text="LR Tools:", icon='MODIFIER_ON')


# PANEL APPEND - BLENDER MENU
def scene_pt_unit(self,context):
    layout = self.layout
    layout.separator()
    layout.operator(scene.SCENE_OT_lr_set_scene_scale_to_meters.bl_idname)

def topbar_mt_file(self, context):
    layout = self.layout
    layout.operator(window.OPN_OT_open_folder.bl_idname)
    layout.operator(window.OPN_OT_open_config.bl_idname)
 
def object_menu_select_curve_bevel(self, context):
    obj = context.active_object
    if obj and obj.type == 'CURVE' and obj.data.bevel_object is not None:
        self.layout.operator(object.OBJECT_OT_select_bevel_object.bl_idname,
                         text="LR: Select Bevel Object")



def register():
    bpy.types.TOPBAR_MT_file.append(topbar_mt_file)
    bpy.types.SCENE_PT_unit.append(scene_pt_unit)
    bpy.types.VIEW3D_MT_object_context_menu.append(object_menu_select_curve_bevel)
    bpy.types.VIEW3D_MT_object_context_menu.append(add_to_object_context_menu)


def unregister():
    bpy.types.VIEW3D_MT_object_context_menu.remove(add_to_object_context_menu)
    bpy.types.VIEW3D_MT_object_context_menu.remove(object_menu_select_curve_bevel)
    bpy.types.SCENE_PT_unit.remove(scene_pt_unit)
    bpy.types.TOPBAR_MT_file.remove(topbar_mt_file)
