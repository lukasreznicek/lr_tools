import bpy,pathlib, subprocess
from bpy.types import Operator



class WM_OT_ToggleTabletAPI(bpy.types.Operator):
    bl_idname = "wm.lr_toggle_tablet_api"
    bl_label = "LR: Toggle Tablet API"

    def execute(self, context):
        prefs = context.preferences.inputs
        prefs.tablet_api = "WINDOWS_INK"
        prefs.tablet_api = "AUTOMATIC"
        bpy.ops.wm.save_userpref()
        self.report({'INFO'}, f"Tablet API now: {prefs.tablet_api}")
        return {'FINISHED'}





# def register():
#     bpy.utils.register_class(ToggleTabletAPI)

# def unregister():
#     bpy.utils.unregister_class(ToggleTabletAPI)

# if __name__ == "__main__":
#     register()


class OPN_OT_open_folder(Operator):
    """Opens Current Folder"""
    bl_idname = "window.open_path"
    bl_label = "Open Current .blend Path"
    bl_description = "Opens Current .blend Path"
    bl_space_type =  "Window"
    bl_region_type = "UI"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        full_path = bpy.path.abspath("//")
        subprocess.Popen('explorer "{0}"'.format(full_path))
        return {'FINISHED'}

class OPN_OT_open_config(Operator):
    """Opens Config Folder"""
    bl_idname = "window.open_config_path"
    bl_label = "Open Startup Path"
    bl_description = "Opens Current .blend Config Path"
    bl_space_type =  "Window"
    bl_region_type = "UI"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        # full_path = bpy.path.abspath("//")
        full_path = bpy.utils.user_resource('CONFIG')
        subprocess.Popen('explorer "{0}"'.format(full_path))
        return {'FINISHED'}



