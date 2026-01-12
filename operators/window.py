import bpy

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
