import bpy,bmesh
from ..utils import lr_functions

class OBJECT_OT_lr_add_attribute(bpy.types.Operator):
    '''Adds a new attribute to all selected objects'''
    bl_idname = "geometry.lr_add_attribute"
    bl_label = "Adds attribute on selected objects"
    bl_options = {'REGISTER', 'UNDO'}


    name: bpy.props.StringProperty(
        name="Name",
        description="Enter a string",
        default="Attribute",
    )

    domain: bpy.props.EnumProperty(
        name="Domain",
        description="Select a domain",
        items=[
            ('POINT', "Vertex", "Add attribute to vertex"),
            ('EDGE', "Edge", "Add attribute to edge"),
            ('FACE', "Face", "Add attribute to face"),
            ('CORNER', "Face Corner", "Add attribute to face corner"),
        ],
        default='POINT',
    )

    data_type: bpy.props.EnumProperty(
        name="Data Type",
        description="Select a data type",
        items=[
            ('FLOAT', "Float", "Float data type"),
            ('INT', "Integer", "Integer data type"),
            ('FLOAT_VECTOR', "Vector", "Vector data type"),
            ('FLOAT_COLOR', "Color", "Color data type"),
            ('BYTE_COLOR', "Byte Color", "Byte Color data type"),
            ('STRING', "String", "String data type"),
            ('BOOLEAN', "Boolean", "Boolean data type"),
            ('FLOAT_2', "2D Vector", "2D Vector data type"),
            ('INT8', "8-Bit Integer", "8-Bit Integer data type"),
            ('INT32_2D', "2D Integer Vector", "2D Integer Vector data type"),
            ('QUATERNION', "Quaternion", "Quaternion data type"),
        ],
        default='FLOAT',
    )

    @classmethod
    def poll(cls, context): 
        return context.mode == 'OBJECT' or context.mode == 'EDIT_MESH'
        
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        count = 0
        for obj in bpy.context.selected_objects:
            if obj.type == 'MESH' or obj.type == 'CURVE' or obj.type == 'EMPTY':

                if obj.data.attributes.get(self.name) == None: #Check if attribute is already present.
                    count+=1
                    obj.data.attributes.new(name=self.name,
                                            type=self.data_type,
                                            domain=self.domain)
        

        self.report({'INFO'}, f'Attribute added  to {count} objects.')
        return {'FINISHED'}		


class OBJECT_OT_lr_remove_attribute(bpy.types.Operator):
    '''Removes an attribute from all selected objects'''
    bl_idname = "geometry.lr_remove_attribute"
    bl_label = "Removes attribute on selected objects"
    bl_options = {'REGISTER', 'UNDO'}


    name: bpy.props.StringProperty(
        name="Name",
        description="Enter a string",
        default="Attribute",
    )


    @classmethod
    def poll(cls, context): 
        return context.mode == 'OBJECT' or context.mode == 'EDIT_MESH'
        
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):

        for obj in bpy.context.selected_objects:
            if obj.type == 'MESH' or obj.type == 'CURVE' or obj.type == 'EMPTY':

                if obj.data.attributes.get(self.name): #Check if attribute is already present.
                    obj.data.attributes.remove(obj.data.attributes[self.name])
                else:
                    message= f'Property: {self.name} not present on object: {obj.name}'
                    self.report({'INFO'}, message)


        return {'FINISHED'}		



class OBJECT_OT_lr_attribute_select_by_index(bpy.types.Operator):
    '''
    
    
    '''
    bl_idname = "geometry.lr_select_attribute_by_index"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

    index: bpy.props.IntProperty(
        name="Index: ",
        description="Enter index to select",
        default=1,
        min=0,
        soft_max=10
    )

    @classmethod
    def poll(cls, context): 
        return context.mode == 'OBJECT' or context.mode == 'EDIT_MESH'
        
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        selected_objects = bpy.context.selected_objects
        bpy.context.object.data.attributes.active_index = self.index
        print(f"{self.index= }")
        for obj in bpy.context.selected_objects:
            obj.data.attributes.active_index = self.index


        return {'FINISHED'}		
    

class OBJECT_OT_lr_attribute_select_by_name(bpy.types.Operator):
    '''
    '''
    bl_idname = "geometry.lr_select_attribute_by_name"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

    attr_name: bpy.props.StringProperty(
        name="Index: ",
        description="Enter index to select",
        default='Attribute',
    )

    @classmethod
    def poll(cls, context): 
        return context.mode == 'OBJECT' or context.mode == 'EDIT_MESH'
        
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):

        for obj in bpy.context.selected_objects:
            for attr in obj.data.attributes:
                if attr.name == self.attr_name:
                    obj.data.attributes.active = attr
            


        return {'FINISHED'}		



# def store_selected_value_into_attr(obj,attr_name, data_type, domain, store_mode):

    



from collections import OrderedDict
from mathutils import Matrix,Vector

class OBJECT_OT_lr_set_obj_info_attr(bpy.types.Operator):
    
    '''
    Works on multiple object selection
    
    Inputs:
        obj: obj 
        attr_name: name of the attribute
        data_type: FLOAT
        domain: POINT
        store_mode: What to store into attribute
            pivot: Stored into first decimal place as a value 1 E.g. .1
            x_axis: Stored into first decimal place as a value 2 E.g. .2
            y_axis: Stored into first decimal place as a value 3 E.g. .3
            element_index: Stored as a whole number before decimal point E.g. 46.

    '''
    bl_idname = "geometry.lr_set_obj_info_attr"
    bl_label = "Store info about object into attribute. Later used by different operator."
    bl_options = {'REGISTER', 'UNDO'}

    attr_name: bpy.props.StringProperty(
        name="Attr Name ",
        description="Enter index to select",
        default='ObjInfo',
    )

    store_mode: bpy.props.EnumProperty(
        items=[
            ('ORIGIN', 'Pivot', 'Use Pivot'),
            ('X_AXIS', 'X Axis', 'Use X Axis'),
            ('Y_AXIS', 'Y Axis', 'Use Y Axis'),
            ('ELEMENT_INDEX', 'Element Index', 'Use Element Index')
        ],
        default='ORIGIN',
        description="Choose store mode"
    )
    enable: bpy.props.BoolProperty(default=True, name = 'Enable', description=' True: assign value. \nFalse: Remove')
    
    @classmethod
    def poll(cls, context): 
        return context.mode == 'OBJECT' or context.mode == 'EDIT_MESH'
        
    skip_invoke: bpy.props.BoolProperty(default=False, options={'HIDDEN'})    
    
    def invoke(self, context, event):
        if self.skip_invoke == True:
            return self.execute(context)
        
        else:
            wm = context.window_manager
            return wm.invoke_props_dialog(self)


    def execute(self, context):

        def modify_decimal_at_index(number, new_decimal, decimal_index):
            # Convert the number to a string
            number_str = "{:.6f}".format(number)

            # Find the position of the decimal point
            decimal_position = number_str.find('.')

            # Check if the number has a decimal point
            if decimal_position != -1:
                # Modify the decimal at the specified index
                modified_number_str = number_str[:decimal_position + decimal_index + 1] + str(new_decimal) + number_str[decimal_position + decimal_index + 2:]
                modified_number = float(modified_number_str)
                return modified_number
            else:
                # If the number has no decimal point, return the original number
                return number


        def get_digit_at_decimal_place(number, decimal_place):
            # Shift the decimal point to the right by the specified decimal place
            shifted_number = number * (10 ** decimal_place)

            # Use modulo to get the digit at the specified decimal place
            digit = int(shifted_number) % 10

            return digit

        for obj_index, obj in enumerate(bpy.context.selected_objects):
            if obj.type == 'MESH':


                obj_attr = obj.data.attributes.get(self.attr_name)

                if obj_attr != None:
                    if obj_attr.domain != 'POINT' or obj_attr.data_type != 'FLOAT': #If attribute with this name is present. Rename if incorrect and make new one.
                        print('Creating')
                        obj_attr.name = self.attr_name+'_Del'
                        obj.data.attributes.new(self.attr_name,type='FLOAT', domain='POINT')
                else:
                    obj.data.attributes.new(self.attr_name,type='FLOAT', domain='POINT')


                if bpy.context.mode == 'OBJECT':
                    bm = bmesh.new()
                    bm.from_mesh(obj.data)           
                if bpy.context.mode == 'EDIT_MESH':
                    bm = bmesh.from_edit_mesh(obj.data)

                # #Create if not present 
                bm_layer = bm.verts.layers.float[self.attr_name]
                # print(f"{bm_layer= }")
                # if bm_layer == None:
                #     bm_layer = bm.verts.layers.float.new(self.attr_name)
                # print(f"{bm_layer= }")

                for vert in bm.verts:
                    if vert.select == True:
                        
                        if self.store_mode == 'ORIGIN':
                            if self.enable == True:
                                vert[bm_layer] = modify_decimal_at_index(vert[bm_layer], 1, 0)
                            else:
                                vert[bm_layer] = modify_decimal_at_index(vert[bm_layer], 0, 0)
                        
                        elif self.store_mode == 'X_AXIS':
                            if self.enable == True:
                                vert[bm_layer] = modify_decimal_at_index(vert[bm_layer], 2, 0)
                            else:
                                vert[bm_layer] = modify_decimal_at_index(vert[bm_layer], 0, 0)
                        elif self.store_mode == 'Y_AXIS':
                            if self.enable == True:
                                vert[bm_layer] = modify_decimal_at_index(vert[bm_layer], 3, 0)
                            else:
                                vert[bm_layer] = modify_decimal_at_index(vert[bm_layer], 0, 0)
                        
                        elif self.store_mode == 'ELEMENT_INDEX':
                            vert[bm_layer] = vert[bm_layer] = obj_index + round(vert[bm_layer] - int(vert[bm_layer]),6)
                    
                    # else:
                    #     if self.store_mode == 'PIVOT':
                    #         if get_digit_at_decimal_place(vert[bm_layer], 1) == 1: #Reset to 0 if value 1 is present at first decimal place on unselected vertex.
                    #             vert[bm_layer] = modify_decimal_at_index(vert[bm_layer], 0, 0)
                    #     elif self.store_mode == 'X_AXIS':
                    #         if get_digit_at_decimal_place(vert[bm_layer], 1) == 2: #Reset to 0 if value 2 is present at first decimal place. 
                    #             vert[bm_layer] = modify_decimal_at_index(vert[bm_layer], 0, 0)
                    #     elif self.store_mode == 'Y_AXIS':
                    #         if get_digit_at_decimal_place(vert[bm_layer], 1) == 3: #Reset to 0 if value 3 is present at first decimal place. 
                    #             vert[bm_layer] = modify_decimal_at_index(vert[bm_layer], 0, 0)

                if bpy.context.mode == 'OBJECT':
                    bm.to_mesh(obj.data)
                if bpy.context.mode == 'EDIT_MESH':
                    bmesh.update_edit_mesh(obj.data)

        bpy.context.view_layer.update() # Ensure changes are displayed in the 3D view
        bm.free()
        return {'FINISHED'}		
    


class OBJECT_OT_lr_recover_obj_info(bpy.types.Operator):
    '''Breaks selected objects into subcomponent based on values in Elements attribute.
    
    Whole number = Subelement index, this list includes indexes mentioned below
    .1 = subelement pivot point.
    .2 = Subelement X axis.
    .3 = Subelement Y axis.
    ._01 = Second and third decimal is parent subelement index. If unspecified parent is index 0'''


    bl_idname = "object.lr_recover_obj_info"
    bl_label = "Get object position and rotation from stored data inside attribute"
    bl_options = {'REGISTER', 'UNDO'}

    remove_extra: bpy.props.BoolProperty(
        name="Remove Extra",
        description="Remove vertices for pivot position. X axis and Y Axis",
        default=False,
    )

    src_attr_name: bpy.props.StringProperty(
        name="Source Attribute",
        description="Attribute with stored obj info data",
        default='ObjInfo',
    )

    # @classmethod
    # def poll(cls, context): 
    #     return context.mode == 'OBJECT' or context.mode == 'EDIT_MESH'
        
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

        
    def execute(self, context): 
        
        @staticmethod
        def parent_objects(child_obj, parent_obj):
            # Store the child object's world matrix
            child_world_matrix = child_obj.matrix_world.copy()

            # Set the child object's parent to the parent object
            child_obj.parent = parent_obj
            child_obj.matrix_world = child_world_matrix  # Restore the world matrix

        @staticmethod
        def vec_to_rotational_matrix(v1,v2,v3):
            """
            type = mathutils.Vector()
            v1,v2,v3 = Vectors for X,Y,Z axis. 
            """
            # Create the rotational matrix
            return Matrix((v1, v2, v3)).transposed()

        @staticmethod
        def gram_schmidt_orthogonalization(v1, v2, v3):
            '''
            Input: 
                mathutils.Vector
            Output:
                mathutils.Vector
            '''
            # Normalize the vectors
            v1.normalize()
            v2.normalize()
            v3.normalize()
            
            # Create the orthogonal basis using Gram-Schmidt orthogonalization
            u1 = v1
            u2 = v2 - (v2.dot(u1) * u1)
            u2.normalize()
            u3 = v3 - (v3.dot(u1) * u1) - (v3.dot(u2) * u2)
            u3.normalize()
            
            orthogonal_vector_basis = (u1, u2, u3)
            return orthogonal_vector_basis

        @staticmethod
        def calculate_z_vector(v1, v2):
            # Calculate the cross product of v1 and v2
            z_vector = v1.cross(v2)
            z_vector.normalize()
            return z_vector

        @staticmethod
        def set_origin_rotation(obj, rotation_matrix_to):
            '''
            obj:
            object origin that is going to be rotated
            
            Rotational Matrix:
            Matrix without scale and translation influence (bpy.contextobject.matrix_world.to_3x3().normalized().to_4x4())
            
            Requires: mathutils.Matrix
            '''

            matrix_world = obj.matrix_world
            
            Rloc = matrix_world.to_3x3().normalized().to_4x4().inverted() @ rotation_matrix_to

            #Object rotation
            obj.matrix_world = (Matrix.Translation(matrix_world.translation) @ rotation_matrix_to @ Matrix.Diagonal(matrix_world.to_scale()).to_4x4())
            
            #Mesh rotation
            obj.data.transform(Rloc.inverted())

        @staticmethod
        def local_to_global_directional_vector(obj, local_vector):
            '''
            Translation of the object does not matter. Purely for rotation
            vector points one unit from object origin.
            
            '''
            # Ensure the object is valid and has a matrix
            if not isinstance(obj, bpy.types.Object) or not obj.matrix_world:
                raise ValueError("Invalid object or object has no world matrix")

            # Create a 4x4 matrix representing the object's world transformation
            world_matrix = obj.matrix_world

            # Convert the local vector to a 4D vector (homogeneous coordinates)
            local_vector_homogeneous = local_vector.to_4d()

            # Multiply the local vector by the object's world matrix to get the global vector
            global_vector_homogeneous = world_matrix @ local_vector_homogeneous

            # Convert the resulting 4D vector back to a 3D vector (removing homogeneous coordinate)
            global_vector = global_vector_homogeneous.to_3d()

            return global_vector

        @staticmethod
        def matrix_decompose(matrix_world):
            ''' 
            returns active_obj_mat_loc, active_obj_mat_rot, active_obj_mat_sca 
            reconstruct by loc @ rotQuat @ scale 
            '''
            
            loc, rotQuat, scale = matrix_world.decompose()

            active_obj_mat_loc = Matrix.Translation(loc)
            active_obj_mat_rot = rotQuat.to_matrix().to_4x4()
            active_obj_mat_sca = Matrix()
            for i in range(3):
                active_obj_mat_sca[i][i] = scale[i]

            return active_obj_mat_loc, active_obj_mat_rot, active_obj_mat_sca

        @staticmethod
        def move_origin_to_coord(obj,x,y,z):
            '''
            Input is global x,y,z mathutils.Vector()
            
            '''
            co_translation_vec = Vector((x,y,z))

            obj_translation_vec = obj.matrix_world.to_translation()
            obj_mat_loc, obj_mat_rot, obj_mat_sca = matrix_decompose(obj.matrix_world)
            
            mat_co = Matrix.Translation((x,y,z))


            new_mat = mat_co @ obj_mat_rot @ obj_mat_sca
            new_mat_mesh = new_mat.inverted() @ obj.matrix_world
            
            
            obj.matrix_world = new_mat

            is_object = True
            if bpy.context.object.mode !='OBJECT':
                is_object = False
                store_mode = bpy.context.object.mode
                bpy.context.object.mode = 'OBJECT'

            obj.data.transform(new_mat_mesh)

            if is_object == False:
                bpy.context.object.mode = store_mode
        
        @staticmethod
        def get_global_vector_position(obj, vector):
            """
            Get the global vertex position for a given object and vertex index.
            
            Parameters:
            obj (bpy.types.Object): The object containing the vertex.
            vertex_index (int): The index of the vertex.
            
            Returns:
            mathutils.Vector: The vertex position in global space.
            """
            if not obj or obj.type != 'MESH':
                # print("Invalid object or not a mesh.")
                return None
            
            return obj.matrix_world @ vector
        
        @staticmethod
        def average_vectors(list_of_vectors:list): 

            local_vertex_co = Vector((0.0, 0.0, 0.0))

            for vector in list_of_vectors:
                local_vertex_co += vector

            return local_vertex_co / len(list_of_vectors)

        @staticmethod
        def element_separate(obj,element_indexes,parent = None, origin_coords = None):
            '''
            Removes one element
            Parameters:
            obj (bpy.types.Object): The object containing the vertex.
            element_indexes [int,int...]: vertex index list that is going to be detached
            
            Returns:
            (bpy.types.Object): Detached mesh with only specified indexes.
            '''

            if obj.type == 'MESH':

                selected_obj = bpy.context.selected_objects
                active_obj = bpy.context.active_object
                bpy.ops.object.select_all(action='DESELECT')

                bpy.context.view_layer.objects.active = obj
                obj.select_set(True)


                bpy.ops.object.duplicate()
                obj_separated = bpy.context.object

                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='DESELECT')
                bpy.ops.object.mode_set(mode='OBJECT')


                for vert in obj_separated.data.vertices:
                    if vert.index not in element_indexes:
                        vert.select = True

                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.delete(type='VERT')
                bpy.ops.object.mode_set(mode='OBJECT')            

                if origin_coords !=None:
                    move_origin_to_coord(obj_separated,
                                         origin_coords[0],
                                         origin_coords[1],
                                         origin_coords[2])

                #parent
                if parent !=None:
                    parent_objects(obj_separated,parent)

                


                #restore selection
                bpy.ops.object.select_all(action='DESELECT')
                for obj in selected_obj:
                    obj.select_set(True)
                bpy.context.view_layer.objects.active = active_obj
            
            return obj_separated

        objs = bpy.context.selected_objects
        
        depsgraph = bpy.context.evaluated_depsgraph_get()


        for obj in objs:
            # obj.data = obj.data.copy() #Make object unique. Remove instancing.
            # # print(f'{obj.data.users = }')
            # act_obj = bpy.context.active_object
            # bpy.context.view_layer.objects.active = obj
            # for modifier in obj.modifiers: # Apply all modifier
            #     bpy.ops.object.modifier_apply(modifier=modifier.name)
            # bpy.context.view_layer.objects.active = act_obj

            obj_evaluated = obj.evaluated_get(depsgraph)  #modifiers need to be applied before taking eny info from them such as coordinates. .co does not include modifiers.
            
            if obj.parent:
                init_parent = obj.parent
            else:
                init_parent = None

            attribute = obj_evaluated.data.attributes.get(self.src_attr_name)

            if attribute == None:
                message = f'Attribute {self.src_attr_name} not found on {obj.name}. Skipping.'
                self.report({'INFO'}, message)
                continue


            

            # 0  = Parent object, 
            # Whole number = subelement index, this list includes indexes mentioned below
            # .1 = subelement pivot point.
            # .2 = Subelement X axis.
            # .3 = Subelement Y axis.
            attr_info = {}
            sub_element_len = 0
            for index,data in enumerate(attribute.data):
                i_val = round(data.value,3)
                # print(f'ATTRIBUTE DATA: \n{i_val}')
                i_val_int = int(i_val)

                if i_val_int not in attr_info:
                    attr_info[i_val_int] = {
                        'index': [],
                        'pivot_index': [],
                        'x_axis_index': [],
                        'y_axis_index': [],
                        'parent_element_id': None,
                        'object':None
                    }

                attr_info[i_val_int]['index'].append(index)

                if round(i_val%1,1) == 0.1:
                    sub_element_len += 1
                    attr_info[i_val_int]['pivot_index'].append(index) #Vertex index that belongs to Pivot. Find: vertex[index].co
                    attr_info[i_val_int]['parent_element_id'] = int(100*(round(i_val*10%1,2))) #This number points to a key in this dictionary. (Parent obj).
                if round(i_val%1,1) == 0.2:
                    attr_info[i_val_int]['x_axis_index'].append(index) #Vertex index where x axis points to.
                if round(i_val%1,1) == 0.3:
                    attr_info[i_val_int]['y_axis_index'].append(index) #Vertex index where Y axis points to.

            attr_info_ordered = OrderedDict(sorted(attr_info.items(), key=lambda x: x[0]))



            pivot_position = []

            for idx in attr_info_ordered: #idx is int



                # ------------------ GET ORIGIN LOCAL AND GLOBAL POSITION FROM VERTEX INDEXES + AVERAGED VERSION ------------------

                origin_idx_len = len(attr_info_ordered[idx]['pivot_index'])

                if origin_idx_len == 1: # No need to average vectors if only one vert index.
                    origin_vector_local_avg = obj_evaluated.data.vertices[attr_info_ordered[idx]['pivot_index'][0]].co
                    origin_vector_global_avg =  get_global_vector_position(obj_evaluated,origin_vector_local_avg)
                
                elif origin_idx_len > 1: # Averaged origin vectors
                    origin_vectors_local = [obj_evaluated.data.vertices[vert_idx].co for vert_idx in attr_info_ordered[idx]['pivot_index']]
                    origin_vector_local_avg = average_vectors(origin_vectors_local)
                    origin_vector_global_avg =  get_global_vector_position(obj_evaluated,origin_vector_local_avg)
                
                else:
                    self.report({'ERROR'}, "Missing Origin Attribute.")
                    continue



                # ------------------ ORIGIN ROTATION GET ------------------

                # ------ Get Directional Vector X from  vertex positions + averaged version ------
                x_axis_idx_len = len(attr_info_ordered[idx]['x_axis_index'])
                if x_axis_idx_len == 1: # No need to average vectors if only one vert index.
                    x_axis_vector_local = obj_evaluated.data.vertices[attr_info_ordered[idx]['x_axis_index'][0]].co

                    directional_vector_x = (obj_evaluated.matrix_world @ x_axis_vector_local) - (obj_evaluated.matrix_world @ origin_vector_local_avg)
                
                elif x_axis_idx_len > 1: #Averaged vectors in case of multiple vertex idx.
                    x_axis_vectors_local = [obj_evaluated.data.vertices[vert_idx].co for vert_idx in attr_info_ordered[idx]['x_axis_index']]
                    x_axis_vector_local_avg = average_vectors(x_axis_vectors_local)

                    directional_vector_x = (obj_evaluated.matrix_world @ x_axis_vector_local_avg) - (obj_evaluated.matrix_world @ origin_vector_local_avg)
                
                else:
                    self.report({'ERROR'}, "Missing X Axis Attribute")
                    continue



                # ------  Get Directional Vector Y  ------

                y_axis_idx_len = len(attr_info_ordered[idx]['y_axis_index'])
                if y_axis_idx_len == 1: 
                    y_axis_vector_local = obj_evaluated.data.vertices[attr_info_ordered[idx]['y_axis_index'][0]].co
                    
                    directional_vector_y = (obj_evaluated.matrix_world @ y_axis_vector_local) - (obj_evaluated.matrix_world @ origin_vector_local_avg) 
                
                elif y_axis_idx_len > 1: #Averaged version
                    y_axis_vectors_local = [obj_evaluated.data.vertices[vert_idx].co for vert_idx in attr_info_ordered[idx]['y_axis_index']]
                    y_axis_vector_local_avg = average_vectors(y_axis_vectors_local)
                    
                    directional_vector_y = (obj_evaluated.matrix_world @ y_axis_vector_local_avg) - (obj_evaluated.matrix_world @ origin_vector_local_avg)
                
                else:
                    self.report({'ERROR'}, "Missing Y Axis Attribute")
                    continue


                #Get Directional Vector Z
                if attr_info_ordered[idx]['pivot_index'] != []:
                    directional_vector_z = obj_evaluated.data.vertices[attr_info_ordered[idx]['pivot_index'][0]].normal @ obj_evaluated.matrix_world.inverted()
                    directional_vector_z = directional_vector_z.normalized()
                else:
                    self.report({'ERROR'}, "Missing pivot position. Vert _.1")
                    continue

                orthagonal_xyz_axis =gram_schmidt_orthogonalization(directional_vector_x, directional_vector_y, directional_vector_z)
                
                #Rotational matrix from orthagonal axis vectors
                rotational_matrix = vec_to_rotational_matrix(orthagonal_xyz_axis[0],orthagonal_xyz_axis[1],orthagonal_xyz_axis[2])

                if self.remove_extra: #Remove verticies which belong to pivot point x axis and y axis. 
                    for vert_idx in attr_info_ordered[idx]['x_axis_index']:
                        attr_info_ordered[idx]['index'].remove(vert_idx)

                    for vert_idx in attr_info_ordered[idx]['y_axis_index']:
                        attr_info_ordered[idx]['index'].remove(vert_idx)                    
                
                    for vert_idx in attr_info_ordered[idx]['pivot_index']:
                        attr_info_ordered[idx]['index'].remove(vert_idx)






                # ------ DUPLICATE ELEMENT ------
                element = lr_functions.duplicate_obj(obj,
                                                     depsgraph=depsgraph,
                                                     name=obj.name + '_part' + '_'+str(idx),
                                                     apply_modifiers=True, #already applying above
                                                     same_transform=True)
                
                # ------ REMOVE ALL BUT NEEDED INDEXES ------
                lr_functions.delete_verts(element,attr_info_ordered[idx]['index'],invert=True)


                attr_info_ordered[idx]['object'] = element #Assign detached object to dictionary


                # ------------ SET ORIGIN POSITION ------------
                if origin_vector_global_avg:
                    
                    move_origin_to_coord(element,
                                         origin_vector_global_avg[0],
                                         origin_vector_global_avg[1],
                                         origin_vector_global_avg[2])

                # ------------ SET ORIGIN ROTATION ------------
                set_origin_rotation(element,rotational_matrix.to_4x4())


            # ------------  SELECT ALL, MAKE ID0 ACTIVE AND PARENT  ------------
            for idx in attr_info_ordered:
                    
                attr_info_ordered[idx]['object'].select_set(True)
                if idx == 0:
                    bpy.context.view_layer.objects.active = attr_info_ordered[idx]['object']
                    
                    if init_parent != None: #Set Index 0 as a child of the original parent.
                        parent_objects(attr_info_ordered[idx]['object'],init_parent)

                if attr_info_ordered[idx]['parent_element_id'] != None: 

                    if attr_info_ordered[idx]['parent_element_id'] != idx:
                        parent_id = attr_info_ordered[idx]['parent_element_id']
                        parent_objects(attr_info_ordered[idx]['object'], attr_info_ordered[parent_id]['object']) 



            #Remove original object
            for col in obj.users_collection:
                col.objects.unlink(obj)

            bpy.data.objects.remove(obj)
            


        return {'FINISHED'}





class OBJECT_OT_lr_attribute_increment_int_values(bpy.types.Operator):
    '''On Active attribute\nMultiple object selection. Active int attributes will be incremented on vertex domain per object. Decimal values stay unchanged.\nActive object gets 0'''
    bl_idname = "geometry.lr_set_per_obj_attribute"
    bl_label = "Increments int attribute on vertex domain"
    bl_options = {'REGISTER', 'UNDO'}



    @classmethod
    def poll(cls, context): 
        return context.mode == 'OBJECT' or context.mode == 'EDIT_MESH'
        
    # def invoke(self, context, event):
    #     wm = context.window_manager
    #     return wm.invoke_props_dialog(self)

    def execute(self, context):
        selected_objects = bpy.context.selected_objects
        selected_objects.remove(bpy.context.active_object)
        selected_objects.insert(0,bpy.context.active_object) #Make sure active object is first in the list

        for index,obj in enumerate(selected_objects):
            for attribute in obj.data.attributes.active.data:
                attribute.value = attribute.value%1.0 + index

        return {'FINISHED'}
