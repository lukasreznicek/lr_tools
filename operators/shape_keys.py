import bpy

class OBJECT_OT_SwitchShapeKeyOnMultipleObjects(bpy.types.Operator):
    """Switch to specified shape key index for selected mesh objects"""
    bl_idname = "object.lr_switch_shape_key_on_multiple_objects"
    bl_label = "Switch Shape Key On Multiple Objects"
    bl_options = {'REGISTER', 'UNDO'}
    
    shape_key_index: bpy.props.IntProperty(
        name="Shape Key Index",
        description="Index of the shape key to switch to",
        default=0,
        min=0,
        soft_max=5
    )

    def execute(self, context):
        for obj in context.selected_objects:
            if obj.type != 'MESH':
                continue

            if obj.data.shape_keys and len(obj.data.shape_keys.key_blocks) > self.shape_key_index:
                obj.active_shape_key_index = self.shape_key_index
            else:
                self.report({'WARNING'}, f"Object {obj.name} does not have shape key index {self.shape_key_index}")

        return {'FINISHED'}
