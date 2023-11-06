import bpy


class lr_vertex_rgb_to_alpha(bpy.types.Operator):
    """Assigns vertex alpha rom RGB value"""
    bl_idname = "lr.assign_vertex_alpha"
    bl_label = "Assigns vertex alpha from RGB value"
    bl_options = {'REGISTER', 'UNDO'}

    # @classmethod
    # def poll(cls, context):
    #     return context.mode == 'EDIT_MESH'


    def update_int_from_float(self,context):
        self['color_a_int'] = int(round(self['color_a'] * 255))


    def update_float_from_int(self,context):
        self['color_a'] = self['color_a_int'] / 255


    color_a: bpy.props.FloatProperty(name = 'Alpha',description = 'Alpha',default = 1.0,min = 0,soft_max = 1, update = update_int_from_float)
    color_a_int: bpy.props.IntProperty(name = 'Alpha (0-255)',description = 'Alpha', default = 255,min = 0, soft_max=255, update = update_float_from_int)


    def execute(self, context):

        mode_store = bpy.context.object.mode
        bpy.ops.object.mode_set(mode='OBJECT')



        def set_alpha_color(active_object):
            #active_object = bpy.context.active_object

            color_attributes = []
            #Get color attributes
            for attr in active_object.data.attributes:  
                if attr.data_type == 'FLOAT_COLOR' or attr.data_type == 'BYTE_COLOR':
                    color_attributes.append(attr)
            
            #Create new attr if not present
            if len(color_attributes) == 0:
                active_object.data.attributes.new('VertexColor', 'FLOAT_COLOR', 'CORNER')

            #Get active Color Attribute. Might be replaced by ordinary attribute by Blender later on.
            active_color_attr = active_object.data.attributes.active_color  #active_color vs active. Latter is attribute
            
            if active_color_attr == None:
                self.report({'WARNING'}, "Select Color Attribute.")
                return {'FINISHED'}
            
            if active_color_attr.domain != 'CORNER':
                self.report({'WARNING'}, "Convert Color Attribute from Vertex to Face Corner.")
                return {'FINISHED'}


            def apply_vertex_alpha(a):
                for i in active_object.data.loops:
                    numb = i.vertex_index
                    index = i.index
                    
                    if active_object.data.vertices[numb].select:
                        active_color_attr.data[index].color[3] = a

                self.report({'INFO'}, 'Alpha set: '+ str(round(a, 2)))
                
            def apply_face_alpha(a):
                for i in active_object.data.polygons:
                    if i.select:

                        for j in i.loop_indices:
                            active_color_attr.data[j].color[3] = a

                self.report({'INFO'}, 'Alpha set: '+ str(round(a, 2)))



            if bpy.context.tool_settings.mesh_select_mode[0]:
                selection_mode = 0
            if bpy.context.tool_settings.mesh_select_mode[1]:
                selection_mode = 1
            if bpy.context.tool_settings.mesh_select_mode[2]:
                selection_mode = 2

            if selection_mode == 0:
                apply_vertex_alpha(self.color_a)

            elif selection_mode == 1:
                #self.report({'ERROR'}, "Please set selection mode to vertices or faces.")
                apply_vertex_alpha(self.color_a)

            elif selection_mode == 2:
                apply_face_alpha(self.color_a)
            else:
                apply_vertex_alpha(self.color_a)
                #self.report({'ERROR'}, "Incorrect selection mode.")


        for object in bpy.context.selected_objects:
            if object.type == 'MESH':
                set_alpha_color(object)

        

        #Restore mode
        bpy.ops.object.mode_set(mode=mode_store)

        return {'FINISHED'}


















