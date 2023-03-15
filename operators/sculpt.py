import bpy

class lr_multires_sculpt_offset(bpy.types.Operator):
    """Decreases or increases subdividion on multires modifier"""
    bl_idname = "lr.offset_multires_sculpt_subd"
    bl_label = "Up or down subdividion on multires modifier."
    bl_options = {'REGISTER', 'UNDO'}

    #Property
    decrease: bpy.props.BoolProperty(name = 'Decrease SubD', description = 'Lowers sculpt SubD on multires modifier', default = False)
    
    # @classmethod
    # def poll(cls, context):
    #     return context.mode == 'EDIT_MESH'   

    def execute(self, context):


        active_obj = bpy.context.object

        for modifier in active_obj.modifiers:
            
            if modifier.type == 'MULTIRES':

                if self.decrease:

                    modifier.sculpt_levels -= 1
                else:  

                    modifier.sculpt_levels += 1

        return {'FINISHED'}