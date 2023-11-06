import bpy



class OBJECT_OT_lr_assign_vertex_color(bpy.types.Operator):
    """Assigns color to selected vertex or face."""
    bl_idname = "lr.assign_vertex_color"
    bl_label = "Assigns color to selected vertex or face."
    bl_options = {'REGISTER', 'UNDO'}


    def update_int_from_float(self, context):
        self['color_r_int'] = int(round(self['color_r'] * 255))
        self['color_g_int'] = int(round(self['color_g'] * 255))
        self['color_b_int'] = int(round(self['color_b'] * 255))
        
        # print('COLOR  INT: ',self['color_r_int'])
        # print(f'UPDATING Int because of the change in Float')


    def update_float_from_int(self, context):
        self['color_r'] = self['color_r_int'] / 255
        self['color_g'] = self['color_g_int'] / 255
        self['color_b'] = self['color_b_int'] / 255
        
        # print('COLOR FLOAT: ',self['color_r'])
        # print(f'UPDATING Float because of the change in Int')
        
    
    set_r: bpy.props.BoolProperty(name = 'Set Red', description = "False: Red channel won't be affected", default = True)
    set_g: bpy.props.BoolProperty(name = 'Set Green', description = "False: Green channel won't be affected", default = True)
    set_b: bpy.props.BoolProperty(name = 'Set Blue', description = "False: Blue channel won't be affected", default = True)

    color_r: bpy.props.FloatProperty(name = 'R (0-1): ',description = 'Red',min = 0, soft_max=1,default=1, update = update_int_from_float)
    color_g: bpy.props.FloatProperty(name = 'G (0-1): ' , description = 'Green',min = 0, soft_max = 1,default=1, update = update_int_from_float)
    color_b: bpy.props.FloatProperty(name = 'B (0-1): ', description = 'Blue', min = 0, soft_max = 1,default=1, update = update_int_from_float)    

    color_r_int: bpy.props.IntProperty(name = 'R (0-255): ',description = 'Red', default = 255,min = 0, soft_max=255, update = update_float_from_int)
    color_g_int: bpy.props.IntProperty(name = 'G (0-255): ', description = 'Green', default = 255, min = 0, max = 255, update = update_float_from_int)
    color_b_int: bpy.props.IntProperty(name = 'B (0-255): ', description = 'Blue', default = 255, min = 0, max = 255, update = update_float_from_int)

    

    def execute(self, context):

        mode_store = bpy.context.object.mode
        bpy.ops.object.mode_set(mode='OBJECT')

        def set_vertex_color(active_object, set_r = True, set_g = True, set_b = True):
            ''' Object needs to be in object mode. '''

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

            def apply_vertex_color(r,g,b): #Going over all loops and checking if vertex is selected. Not possible to get loops from vertex. 

                for loop in active_object.data.loops: #BMesh version would be better. BMesh can reitrive connected loops to a vertex.
                    vert_index = loop.vertex_index
                    loop_index = loop.index

                    if active_object.data.vertices[vert_index].select: #Check if loop belongs to selected vertex

                        if set_r == True:
                            active_color_attr.data[loop_index].color[0] = r

                        if set_g == True:
                            active_color_attr.data[loop_index].color[1] = g
                        
                        if set_b == True:
                            active_color_attr.data[loop_index].color[2] = b


            def apply_face_color(r,g,b):
                for polygon in active_object.data.polygons:
                    
                    if polygon.select:
                        for loop_index in polygon.loop_indices:
                            
                            if set_r == True:
                                active_color_attr.data[loop_index].color[0] = r
                            
                            if set_g == True:
                                active_color_attr.data[loop_index].color[1] = g

                            if set_b == True:
                                active_color_attr.data[loop_index].color[2] = b


            if bpy.context.tool_settings.mesh_select_mode[0]:
                selection_mode = 0
            if bpy.context.tool_settings.mesh_select_mode[1]:
                selection_mode = 1
            if bpy.context.tool_settings.mesh_select_mode[2]:
                selection_mode = 2
                            

            if selection_mode == 0:
                apply_vertex_color(self.color_r,
                                   self.color_g,
                                   self.color_b)

            elif selection_mode == 1:
                apply_vertex_color(self.color_r,
                                   self.color_g,
                                   self.color_b)
                # self.report({'ERROR'}, "Please set selection mode to vertices or faces.")

            elif selection_mode == 2:
                apply_face_color(self.color_r,
                                 self.color_g,
                                 self.color_b)
            else:
                self.report({'ERROR'}, "Incorrect selection mode.")


        for object in bpy.context.selected_objects:
            if object.type == 'MESH':
                set_vertex_color(object, set_r = self.set_r, set_g = self.set_g, set_b = self.set_b)


        bpy.ops.object.mode_set(mode=mode_store)


        return {'FINISHED'} 

    def draw(self, context):
        
    
        # Create a row layout for the boolean properties
        layout = self.layout
        row = layout.row(align=True)
        row.prop(self, 'set_r')
        row = layout.row(align=True)
        row.prop(self, 'color_r')
        row.prop(self, 'color_r_int')

        row = layout.row(align=True)
        row.prop(self, 'set_g')
        row = layout.row(align=True)
        row.prop(self, 'color_g')
        row.prop(self, 'color_g_int')

        row = layout.row(align=True)
        row.prop(self, 'set_b')
        row = layout.row(align=True)
        row.prop(self, 'color_b')
        row.prop(self, 'color_b_int')







class lr_offset_vertex_color(bpy.types.Operator):
    """Offsets color to selected vertex or face."""
    bl_idname = "lr.offset_vertex_color"
    bl_label = "Offsets color on selected vertexes or faces."
    bl_options = {'REGISTER', 'UNDO'}

    #Property
    invert: bpy.props.BoolProperty(name = 'invert', description = 'Invert', default = False)
    
    # @classmethod
    # def poll(cls, context):
    #     return context.mode == 'EDIT_MESH'   

    def execute(self, context):

        offset_amount_all = bpy.context.scene.lr_tools.vertex_color_offset_amount

        mode_store = bpy.context.object.mode

        if mode_store != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')


        def offset_vc_on_object(active_object):
            #active_object = bpy.context.active_object
            
            if len(active_object.data.vertex_colors.values()) == 0:
                active_object.data.vertex_colors.new()

            color_layer = active_object.data.vertex_colors.active  

            if bpy.context.tool_settings.mesh_select_mode[0]:
                selection_mode = 0
            if bpy.context.tool_settings.mesh_select_mode[1]:
                selection_mode = 1
            if bpy.context.tool_settings.mesh_select_mode[2]:
                selection_mode = 2


            def offset_vertex_color():
                r_color_vert = []
                g_color_vert = []
                b_color_vert = []
                
                for i in active_object.data.loops:
                    numb = i.vertex_index
                    index = i.index
                    
                    if active_object.data.vertices[numb].select:
                        alpha_value = color_layer.data[index].color[3]
                    
                        if self.invert == False:
                            color_layer.data[index].color[0] += offset_amount_all
                            color_layer.data[index].color[1] += offset_amount_all
                            color_layer.data[index].color[2] += offset_amount_all
                            color_layer.data[index].color[3] = alpha_value

                        if self.invert == True:
                            color_layer.data[index].color[0] -= offset_amount_all
                            color_layer.data[index].color[1] -= offset_amount_all
                            color_layer.data[index].color[2] -= offset_amount_all
                            color_layer.data[index].color[3] = alpha_value


                        #Clamp values to range 0 to 1
                        max(min(color_layer.data[index].color[0], 1), 0)
                        max(min(color_layer.data[index].color[1], 1), 0)
                        max(min(color_layer.data[index].color[2], 1), 0)

                        #Collecting for average color
                        r_color_vert.append(color_layer.data[index].color[0])
                        g_color_vert.append(color_layer.data[index].color[1])
                        b_color_vert.append(color_layer.data[index].color[2])

                return r_color_vert,g_color_vert,b_color_vert


            def offset_face_color():
                r_color_face = []
                g_color_face = []
                b_color_face = []
                for i in active_object.data.polygons:
                    if i.select:

                        for j in i.loop_indices:
                            alpha_value = color_layer.data[j].color[3]

                            if self.invert == False:
                                color_layer.data[j].color[0] += offset_amount_all
                                color_layer.data[j].color[1] += offset_amount_all
                                color_layer.data[j].color[2] += offset_amount_all
                                color_layer.data[j].color[3] = alpha_value

                            if self.invert == True:
                                color_layer.data[j].color[0] -= offset_amount_all
                                color_layer.data[j].color[1] -= offset_amount_all
                                color_layer.data[j].color[2] -= offset_amount_all
                                color_layer.data[j].color[3] = alpha_value


                            #Clamp values to range 0 to 1
                            max(min(color_layer.data[j].color[0], 1), 0)
                            max(min(color_layer.data[j].color[1], 1), 0)
                            max(min(color_layer.data[j].color[2], 1), 0)

                            #Collecting for average color
                            r_color_face.append(color_layer.data[j].color[0])
                            g_color_face.append(color_layer.data[j].color[1])
                            b_color_face.append(color_layer.data[j].color[2])
                return r_color_face,g_color_face,b_color_face



            if selection_mode == 0:
                r_color_vert,g_color_vert,b_color_vert = offset_vertex_color()
                r_color_average = [sum(r_color_vert) / len(r_color_vert)]
                g_color_average = [sum(g_color_vert) / len(g_color_vert)]
                b_color_average = [sum(b_color_vert) / len(b_color_vert)]

                self.report({'INFO'}, "Average: "+ '    R: ' +str(round(r_color_average[0],2)) + '    G: '+ str(round(g_color_average[0],2)) + '    B: ' + str(round(b_color_average[0],2)))
                


            elif selection_mode == 1:
                r_color_vert,g_color_vert,b_color_vert = offset_vertex_color()
                r_color_average = [sum(r_color_vert) / len(r_color_vert)]
                g_color_average = [sum(g_color_vert) / len(g_color_vert)]
                b_color_average = [sum(b_color_vert) / len(b_color_vert)]

                self.report({'INFO'}, "Average: "+ '    R: ' +str(round(r_color_average[0],2)) + '    G: '+ str(round(g_color_average[0],2)) + '    B: ' + str(round(b_color_average[0],2)))
                

            elif selection_mode == 2:
                r_color_face, g_color_face, b_color_face = offset_face_color()
                r_color_average = [sum(r_color_face) / len(r_color_face)]
                g_color_average = [sum(g_color_face) / len(g_color_face)]
                b_color_average = [sum(b_color_face) / len(b_color_face)]
                
                self.report({'INFO'}, "Average: "+ '    R: ' +str(round(r_color_average[0],2)) + '    G: '+ str(round(g_color_average[0],2)) + '    B: ' + str(round(b_color_average[0],2)))
            else:
                self.report({'ERROR'}, "Incorrect selection mode.")




        for object in bpy.context.selected_objects:
            offset_vc_on_object(object)


        bpy.ops.object.mode_set(mode=mode_store)

        return {'FINISHED'}

class lr_pick_vertex_color(bpy.types.Operator):
    """Pick vertex color from active polygon"""
    bl_idname = "lr.pick_vertex_color"
    bl_label = "Pick vertex color or alpha"
    bl_options = {'REGISTER', 'UNDO'}

    
    @classmethod
    def poll(cls, context):
        return bpy.context.tool_settings.mesh_select_mode[2]   
    
    #property
    pick_alpha: bpy.props.BoolProperty(name = 'Pick Alpha', description='Outputs alpha', default = False)

    def execute(self, context):
        
        active_object = bpy.context.object
        mode_store = active_object.mode
        bpy.ops.object.mode_set(mode='OBJECT')

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

        active_polygon = active_object.data.polygons[active_object.data.polygons.active]

        loop_indices = [i for i in active_polygon.loop_indices]

        #collect colors
        colors = [active_color_attr.data[i].color for i in loop_indices]

        r = g = b = a = 0
        
        for color in colors:
            r += color[0]
            g += color[1]            
            b += color[2]
            a += color[3]
        r /= active_polygon.loop_total
        g /= active_polygon.loop_total
        b /= active_polygon.loop_total
        a /= active_polygon.loop_total

        if self.pick_alpha == False:
            bpy.context.tool_settings.image_paint.brush.color[0] = r
            bpy.context.tool_settings.image_paint.brush.color[1] = g
            bpy.context.tool_settings.image_paint.brush.color[2] = b

        if self.pick_alpha == True:
            bpy.context.scene.lr_tools.lr_vc_alpha_swatch = a



        bpy.ops.object.mode_set(mode=mode_store)

        return {'FINISHED'}