import bpy

# class lr_multires_sculpt_offset(bpy.types.Operator):
#     """Decreases or increases subdividion on multires modifier"""
#     bl_idname = "lr.offset_multires_sculpt_subd"
#     bl_label = "Up or down subdividion on multires modifier."
#     bl_options = {'REGISTER', 'UNDO'}

#     #Property
#     decrease: bpy.props.BoolProperty(name = 'Decrease SubD', description = 'Lowers sculpt SubD on multires modifier', default = False)
    
#     # @classmethod
#     # def poll(cls, context):
#     #     return context.mode == 'EDIT_MESH'   


#     def execute(self, context):
#         active_obj = bpy.context.object
#         has_modifier = False
#         for modifier in active_obj.modifiers:    
#             if modifier.type == 'MULTIRES':
#                 has_modifier=True
#                 if self.decrease:

#                     modifier.sculpt_levels -= 1
#                 else:  

#                     modifier.sculpt_levels += 1

#         if not has_modifier:
#             active_obj.modifiers.new("Multires","MULTIRES")
#         return {'FINISHED'}
    

class lr_multires_sculpt_offset(bpy.types.Operator):
    """Decreases or increases subdivision on multires modifier"""
    bl_idname = "lr.offset_multires_sculpt_subd"
    bl_label = "Multires edit"   # This is just a placeholder title
    bl_options = {'REGISTER', 'UNDO'}

    decrease: bpy.props.BoolProperty(
        name='Decrease SubD', 
        description='Lowers sculpt SubD on multires modifier',
        default=False
    )

    def has_multires(self, obj):
        return any(mod.type == 'MULTIRES' for mod in obj.modifiers)

    def invoke(self, context, event):
        obj = context.object
        if self.has_multires(obj):
            # No prompt needed, just execute directly
            return self.execute(context)
        else:
            # Show confirmation popup
            return context.window_manager.invoke_props_dialog(self, width=300)
            # return context.window_manager.invoke_confirm(self, event)

    def draw(self, context):
        obj = context.object
        if not self.has_multires(obj):
            self.layout.label(text="Add multires modifier?")
        else:
            self.layout.prop(self, "decrease", text="Decrease subdivision")


    def execute(self, context):
        active_obj = context.object
        has_modifier = False

        for modifier in active_obj.modifiers:    
            if modifier.type == 'MULTIRES':
                has_modifier = True
                if self.decrease:
                    modifier.sculpt_levels = max(0, modifier.sculpt_levels - 1)
                else:  
                    modifier.sculpt_levels += 1

        if not has_modifier:
            active_obj.modifiers.new("Multires","MULTIRES")

        return {'FINISHED'}