import bpy


class lr_vertex_rgb_to_alpha(bpy.types.Operator):
    """Assigns vertex alpha rom RGB value"""
    bl_idname = "lr.assign_vertex_alpha"
    bl_label = "Assigns vertex alpha from RGB value"
    bl_options = {'REGISTER', 'UNDO'}

    # @classmethod
    # def poll(cls, context):
    #     return context.mode == 'EDIT_MESH'

    set_a: bpy.props.FloatProperty(
        name = 'A',
        description = 'Alpha',
        default = 1.0,
        min = 0,
        soft_max = 1,
    )


    def execute(self, context):

        mode_store = bpy.context.object.mode
        bpy.ops.object.mode_set(mode='OBJECT')


        def set_alpha_color(active_object):
            #active_object = bpy.context.active_object

            if len(active_object.data.vertex_colors.items()) == 0:
                active_object.data.vertex_colors.new()
            
            color_layer = active_object.data.vertex_colors.active  



            if bpy.context.tool_settings.mesh_select_mode[0]:
                selection_mode = 0
            if bpy.context.tool_settings.mesh_select_mode[1]:
                selection_mode = 1
            if bpy.context.tool_settings.mesh_select_mode[2]:
                selection_mode = 2


            def apply_vertex_alpha(a):
                for i in active_object.data.loops:
                    numb = i.vertex_index
                    index = i.index
                    
                    if active_object.data.vertices[numb].select:

                        r_value = color_layer.data[index].color[0]
                        g_value = color_layer.data[index].color[1]
                        b_value = color_layer.data[index].color[2]
                        color_layer.data[index].color = (r_value,g_value,b_value,a)
                self.report({'INFO'}, 'Alpha set: '+ str(round(a, 2)))
                
            def apply_face_alpha(a):
                for i in active_object.data.polygons:
                    if i.select:

                        for j in i.loop_indices:
                            r_value = color_layer.data[j].color[0]
                            g_value = color_layer.data[j].color[1]
                            b_value = color_layer.data[j].color[2]
                            color_layer.data[j].color = (r_value,g_value,b_value,a)
                self.report({'INFO'}, 'Alpha set: '+ str(round(a, 2)))

            if selection_mode == 0:
                apply_vertex_alpha(self.set_a)

            elif selection_mode == 1:
                #self.report({'ERROR'}, "Please set selection mode to vertices or faces.")
                apply_vertex_alpha(self.set_a)

            elif selection_mode == 2:
                apply_face_alpha(self.set_a)
            else:
                apply_vertex_alpha(self.set_a)
                #self.report({'ERROR'}, "Incorrect selection mode.")


        active_and_selected_obj = bpy.context.selected_objects
        active_and_selected_obj.append(bpy.context.object)
        for object in active_and_selected_obj:
            if object.type == 'MESH':
                set_alpha_color(object)

        

        #Restore mode
        bpy.ops.object.mode_set(mode=mode_store)

        return {'FINISHED'}


















