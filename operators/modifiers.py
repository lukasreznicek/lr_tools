import bpy
class OBJECT_OT_delete_modifier(bpy.types.Operator):
    bl_idname = "object.delete_modifier"
    bl_label = "Delete Modifier by Name"
    bl_options = {'REGISTER', 'UNDO'}

    modifier_name: bpy.props.StringProperty(name="Name", default="")

    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "modifier_name")


    def execute(self, context):

        for obj in bpy.context.selected_objects:
        
            if obj.type == 'MESH':
                for modifier in obj.modifiers:
                    if modifier.name == self.modifier_name:
                        obj.modifiers.remove(modifier)


                    
        return {'FINISHED'}