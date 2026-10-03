import bpy

def snap_cursor_to_active_with_rotation(context):
    obj = context.active_object
    if obj is None:
        return False

    scene = context.scene
    cursor = scene.cursor

    # Set cursor location to active object's world location
    cursor.location = obj.matrix_world.translation

    # Transfer rotation from object's world matrix to cursor
    # Preserve rotation mode (QUATERNION or Euler)

    if obj.rotation_mode == 'QUATERNION':
        cursor.rotation_mode = 'QUATERNION'
        cursor.rotation_quaternion = obj.matrix_world.to_quaternion()
    else:
        # Use the object's rotation_mode as the Euler order
        cursor.rotation_mode = obj.rotation_mode
        cursor.rotation_euler = obj.matrix_world.to_euler(obj.rotation_mode)
    return True  


class VIEW3D_OT_snap_cursor_to_active(bpy.types.Operator):
    """Snap 3D cursor to active object and copy its world rotation"""
    bl_idname = "view3d.lr_snap_cursor_to_active"
    bl_label = "Snap Cursor to Active (with Rotation)"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        ok = snap_cursor_to_active_with_rotation(context)
        if not ok:
            self.report({'WARNING'}, "No active object to snap to")
            return {'CANCELLED'}
        return {'FINISHED'}




# class VIEW3D_OT_cursor_grab(bpy.types.Operator):
#     """Grab with temporary cursor pivot/orientation"""
#     bl_idname = "view3d.cursor_grab"
#     bl_label = "Cursor Grab (Temporary Settings)"
#     bl_options = {'REGISTER', 'UNDO'}

#     # store old settings
#     # old_pivot: bpy.props.EnumProperty(items=bpy.types.ToolSettings.bl_rna.properties['transform_pivot_point'].enum_items)
#     # old_orient: bpy.props.EnumProperty(items=bpy.types.ToolSettings.bl_rna.properties['transform_orientation_slots'].enum_items)
# # bpy.context.scene.transform_orientation_slots[0].type = 'CURSOR'
#     initial_orient = None
#     initial_pivot = None


#     def invoke(self, context, event):
#         # ts = context.tool_settings

#         # Save current settings
#         self.initial_orient = bpy.context.scene.transform_orientation_slots[0].type
#         self.initial_pivot  = bpy.context.scene.tool_settings.transform_pivot_point
#         # self.old_pivot = ts.transform_pivot_point
#         # self.old_orient = ts.transform_orientation_slots[0].type

#         # Apply temporary settings
#         bpy.context.scene.tool_settings.transform_pivot_point = 'CURSOR'
#         bpy.context.scene.transform_orientation_slots[0].type = 'CURSOR'

#         # Call modal Grab
#         bpy.ops.transform.translate('INVOKE_DEFAULT')

#         # Add a modal handler to detect when Grab finishes
#         context.window_manager.modal_handler_add(self)
#         return {'RUNNING_MODAL'}

#     def modal(self, context, event):
#         # When Grab finishes, Blender sends a FINISHED or CANCELLED event
#         if event.type in {'LEFTMOUSE', 'RIGHTMOUSE', 'ESC'}:
#             # Restore original settings

#             bpy.context.scene.tool_settings.transform_pivot_point= self.initial_pivot
#             bpy.context.scene.transform_orientation_slots[0].type = self.initial_orient

#             return {'FINISHED'}

#         return {'RUNNING_MODAL'}