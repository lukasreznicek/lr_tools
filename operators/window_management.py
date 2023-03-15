# import bpy

# class WINDOW_OT_lr_window_popup(bpy.types.Operator):
#     bl_idname = "wm.lr_window_popup"
#     bl_label = "Opens new window"
#     bl_options = {'REGISTER', 'UNDO'}
    
#     lr_window_editors:bpy.props.EnumProperty(items= (('UV', 'UV', 'UV Editor'), ('ASSET', 'Library', 'Asset Library'), ('ShaderNodeTree', 'Shader', 'Shader Editor')), name = "Editors")   

#     def execute(self, context):
        
        
#         # Modify render settings
#         render = bpy.context.scene.render
#         render.resolution_x = 640
#         render.resolution_y = 480
#         render.resolution_percentage = 100

#         # Modify preferences (to guaranty new window)
#         prefs = bpy.context.preferences
#         prefs.view.render_display_type = "WINDOW"

#         # Call image editor window
#         bpy.ops.render.view_show("INVOKE_DEFAULT")

#         # Change area type
#         area = bpy.context.window_manager.windows[-1].screen.areas[0]
#         area.type = 'VIEW_3D'
#         area.ui_type = self.lr_window_editors
                    
#         return {'FINISHED'}


