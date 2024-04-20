import bpy,bmesh
from ..utils import lr_functions
from collections import OrderedDict
from mathutils import Matrix,Vector
import mathutils

class OBJECT_OT_lr_add_attribute(bpy.types.Operator):
    '''Adds a new attribute to all selected objects'''
    bl_idname = "geometry.lr_add_attribute"
    bl_label = "Adds attribute on selected objects"
    bl_options = {'REGISTER', 'UNDO'}


    name: bpy.props.StringProperty(
        name="Name",
        description="Enter a string",
        default="Attribute",
    )# type: ignore

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
    )# type: ignore

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
    ) # type: ignore

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
    )# type: ignore


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
    )# type: ignore

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
    )# type: ignore

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
    )# type: ignore

    store_mode: bpy.props.EnumProperty(
        items=[
            ('ORIGIN', 'Pivot', 'Use Pivot'),
            ('X_AXIS', 'X Axis', 'Use X Axis'),
            ('Y_AXIS', 'Y Axis', 'Use Y Axis'),
            ('Z_AXIS', 'Y Axis', 'Use Z Axis'),
            ('ELEMENT_INDEX', 'Element Index', 'Use Element Index')
        ],
        default='ORIGIN',
        description="Choose store mode"
    )# type: ignore
    enable: bpy.props.BoolProperty(default=True, name = 'Enable', description=' True: assign value. \nFalse: Remove')# type: ignore
    
    @classmethod
    def poll(cls, context): 
        return context.mode == 'OBJECT' or context.mode == 'EDIT_MESH'
        
    skip_invoke: bpy.props.BoolProperty(default=False, options={'HIDDEN'})    # type: ignore
    
    def invoke(self, context, event):
        if self.skip_invoke == True:
            return self.execute(context)
        
        else:
            wm = context.window_manager
            return wm.invoke_props_dialog(self)


    def execute(self, context):

        @staticmethod
        def change_digit(original_number, position_from_right, new_value):
            # Starting from 0
            # Extract the digits from the original number
            
            if original_number <= 999:
                original_number = 1111

            original_number = int(original_number)
            digits = [int(digit) for digit in str(original_number)]

            # Change the digit at the specified position from the right
            if position_from_right < len(digits):
                digits[-position_from_right - 1] = new_value
            else:
                raise ValueError("Position from right exceeds the number of digits in the original number.")

            # Recreate the new number
            new_number = int(''.join(map(str, digits)))

            return new_number

        # def get_digit(position):
        #     attr_val_y_1 = int(data.vector[1] % 10)            #Z      (Get Ones)
        #     attr_val_y_2 = int(data.vector[1] // 10 % 10)      #Y      (Get Tens)
        #     attr_val_y_3 = int(data.vector[1] // 100 % 10)     #X      (Get Hundreds)
        #     attr_val_y_4 = int(data.vector[1] // 1000 % 10)    #Pivot  (Get Thousands)


        def modify_decimal_at_index(number, new_decimal, decimal_index):
            # Convert the number to a string
            number = round(number,4) #5 decimals are loosing precision needs to be rounded to 4

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
                    if obj_attr.domain != 'CORNER' or obj_attr.data_type != 'FLOAT_VECTOR': #If attribute with this name is present. Rename if incorrect and make new one.
                        obj_attr.name = self.attr_name+'_Del'
                        obj.data.attributes.new(self.attr_name,type='FLOAT_VECTOR', domain='CORNER')
                else:
                    obj.data.attributes.new(self.attr_name,type='FLOAT_VECTOR', domain='CORNER')


                if bpy.context.mode == 'OBJECT':
                    bm = bmesh.new()
                    bm.from_mesh(obj.data)           
                if bpy.context.mode == 'EDIT_MESH':
                    bm = bmesh.from_edit_mesh(obj.data)

                # #Create if not present 
                bm_layer = bm.loops.layers.float_vector[self.attr_name]
                # print(f"{bm_layer= }")
                # if bm_layer == None:
                #     bm_layer = bm.verts.layers.float.new(self.attr_name)
                # print(f"{bm_layer= }")

                select_mode = bm.select_mode   # 'VERT','EDGE','FACE'

                if select_mode == {'VERT'} or select_mode == {'VERT', 'FACE'}:

                    for vert in bm.verts:
                        if vert.select == True:
                            for loop in vert.link_loops:

                                if self.store_mode == 'ORIGIN':
                                    if self.enable == True:
                                        # print(f'{loop[bm_layer][1]= }')
                                        loop[bm_layer][1] = change_digit(loop[bm_layer][1], 3, 2)
                                    else:
                                        loop[bm_layer][1] = change_digit(loop[bm_layer][1], 3, 1)
                                
                                elif self.store_mode == 'X_AXIS':
                                    if self.enable == True:
                                        loop[bm_layer][1] = change_digit(loop[bm_layer][1], 2, 2)
                                    else:
                                        loop[bm_layer][1] = change_digit(loop[bm_layer][1], 2, 1)

                                elif self.store_mode == 'Y_AXIS':
                                    if self.enable == True:
                                        loop[bm_layer][1] = change_digit(loop[bm_layer][1], 1, 2)
                                    else:
                                        loop[bm_layer][1] = change_digit(loop[bm_layer][1], 1, 1)

                                elif self.store_mode == 'Z_AXIS':
                                    if self.enable == True:
                                        loop[bm_layer][1] = change_digit(loop[bm_layer][1], 0, 2)
                                    else:
                                        loop[bm_layer][1] = change_digit(loop[bm_layer][1], 0, 1)


                if select_mode == {'FACE'}:
                    for face in bm.faces:

                        if face.select == True:
                            for loop in face.loops:

                                if self.store_mode == 'ORIGIN':
                                    if self.enable == True:
                                        # print(f'{loop[bm_layer][1]= }')
                                        loop[bm_layer][1] = change_digit(loop[bm_layer][1], 3, 2)
                                    else:
                                        loop[bm_layer][1] = change_digit(loop[bm_layer][1], 3, 1)

                                elif self.store_mode == 'X_AXIS':
                                    if self.enable == True:
                                        loop[bm_layer][1] = change_digit(loop[bm_layer][1], 2, 2)
                                    else:
                                        loop[bm_layer][1] = change_digit(loop[bm_layer][1], 2, 1)

                                elif self.store_mode == 'Y_AXIS':
                                    if self.enable == True:
                                        loop[bm_layer][1] = change_digit(loop[bm_layer][1], 1, 2)
                                    else:
                                        loop[bm_layer][1] = change_digit(loop[bm_layer][1], 1, 1)

                                elif self.store_mode == 'Z_AXIS':
                                    if self.enable == True:
                                        loop[bm_layer][1] = change_digit(loop[bm_layer][1], 0, 2)
                                    else:
                                        loop[bm_layer][1] = change_digit(loop[bm_layer][1], 0, 1)



                if bpy.context.mode == 'OBJECT':
                    bm.to_mesh(obj.data)
                if bpy.context.mode == 'EDIT_MESH':
                    bmesh.update_edit_mesh(obj.data)

        bpy.context.view_layer.update() # Ensure changes are displayed in the 3D view
        bm.free()
        return {'FINISHED'}		
    


class OBJECT_OT_lr_recover_obj_info(bpy.types.Operator):
    '''Breaks selected objects into subcomponent based on values in Elements attribute.
    
    Vector3

    X = Object Index
    Y = (1111.0 = Off, 2222.0 = On) Object pivot, X axis, Y axis, Z axis
    Z = Parent ID
    
    '''

    bl_idname = "object.lr_recover_obj_info"
    bl_label = "Get object position and rotation from stored data inside attribute"
    bl_options = {'REGISTER', 'UNDO'}

    remove_extra: bpy.props.BoolProperty(
        name="Remove Extra",
        description="Remove vertices for pivot position. X axis and Y Axis",
        default=False,
    ) # type: ignore

    fix_left_handed_axis: bpy.props.BoolProperty(
        name = "Fix Axis",
        description = "If resulting axis is left handed, invert Y axis making it right handed. This will prevent negative scaling or flipped normals.",
        default = True,
    ) # type: ignore

    src_attr_name: bpy.props.StringProperty(
        name="Source Attribute",
        description="Attribute with stored obj info data",
        default='ObjInfo',
    ) # type: ignore


    # @classmethod
    # def poll(cls, context): 
    #     return context.mode == 'OBJECT' or context.mode == 'EDIT_MESH'
        
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

        
    def execute(self, context): 
        

        @staticmethod
        def directional_vector_from_loop_indices(
            obj: bpy.types.Object,
            loop_indices: list,
            local_origin: Vector = None) -> mathutils.Vector:
            """
            Takes in local origin
            Calculate a directional vector based on the specified loop indices of a 3D object in Blender.

            Parameters:
            - obj: bpy.types.Object
            The Blender object for which the directional vector is calculated.
            
            - loop_indices: list
            A list of loop indices associated with the object, representing the points used to determine the directional vector.
            
            - local_origin: Vector, optional
            The local origin vector used as a reference point for calculating the directional vector.
            Default is the origin (0, 0, 0).

            Returns:
            - Vector or None
            The calculated directional vector based on the specified loop indices. Returns None if no valid directional vector could be determined.
            """
            if local_origin == None:
                local_origin = Vector((0, 0, 0))

            axis_indices_len = len(loop_indices)

            if axis_indices_len == 1:
                axis_vector_local = obj.data.vertices[obj.data.loops[loop_indices[0]].vertex_index].co
                directional_vector = (obj.matrix_world @ axis_vector_local) - (obj.matrix_world @ local_origin)
                
            elif axis_indices_len > 1:
                vertices_from_loops = list(set([obj.data.loops[loop_idx].vertex_index for loop_idx in loop_indices]))
                axis_vectors_local = [obj.data.vertices[vert_idx].co for vert_idx in vertices_from_loops]
                axis_vectors_local_avg = sum(axis_vectors_local, Vector()) / len(axis_vectors_local) #Averaged version
                directional_vector = (obj.matrix_world @ axis_vectors_local_avg) - (obj.matrix_world @ local_origin)
                
            else:
                directional_vector = None

            return directional_vector


        @staticmethod
        def position_from_loop_indices(obj,
                                       loop_indicies:list):
                                       
            """
            Calculate the local and global average positions, and the average normal vector from the specified loop indices.

            Parameters:
            - obj: bpy.types.Object
            The Blender object for which the positions and normal vector are calculated.

            - loop_indices: list
            A list of loop indices associated with the object, representing the points used to determine the positions and normal vector.

            Returns:
            - Tuple of (Vector, Vector, Vector) or (None, None, None)
            - position_global_avg: The global average position.
            - position_local_avg: The local average position.
            - normal_vector_local: The average normal vector.
            Returns (None, None, None) if no valid origin positions are determined.
            """

            origin_idx_len = len(loop_indicies)

            if origin_idx_len == 1: # No need to average vectors if only one vert index.
                position_local_avg = obj.data.vertices[obj.data.loops[loop_indicies[0]].vertex_index].co
                position_global_avg =  obj.matrix_world @ position_local_avg

                normal_vector_local = obj.data.vertices[obj.data.loops[loop_indicies[0]].vertex_index].normal

            elif origin_idx_len > 1: # Averaged origin vectors

                vertices_from_loops = list(set([obj.data.loops[loop_idx].vertex_index for loop_idx in loop_indicies]))
                origin_positions_local = [obj.data.vertices[vert_idx].co for vert_idx in vertices_from_loops]
                position_local_avg = average_vectors(origin_positions_local)
                position_global_avg =  obj.matrix_world @ position_local_avg

                normal_vector_local = average_vectors([obj.data.vertices[vert_idx].normal for vert_idx in vertices_from_loops])
                
            else:
                position_global_avg = None
                position_local_avg = None
                normal_vector_local = None
                message = f"Missing Origin Attribute on {obj.name}"
                self.report({'INFO'}, message)

            return (position_global_avg, position_local_avg, normal_vector_local)


        @staticmethod
        def change_digit(original_number, position_from_right, new_value):
            # Extract the digits from the original number
            digits = [int(digit) for digit in str(original_number)]

            # Change the digit at the specified position from the right
            if position_from_right < len(digits):
                digits[-position_from_right - 1] = new_value
            else:
                raise ValueError("Position from right exceeds the number of digits in the original number.")

            # Recreate the new number
            new_number = int(''.join(map(str, digits)))

            return new_number


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
            return Matrix((v1, v2, v3)).transposed() #Flip rows into columns. So v1 is in first column instead of a first row.


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
        def is_right_handed(v1, v2, v3):
            # Cross product of v1 and v2
            cross_product = v1.cross(v2) #order matters
            
            # Dot product of the cross product and v3
            dot_product = cross_product.dot(v3)
            
            # Check the sign of the dot product
            if dot_product > 0:
                return True
            elif dot_product < 0:
                return False
            else:
                return None


        @staticmethod
        def set_origin_rotation(obj, rotation_matrix_to):
            '''
            Not Additive. Replaces current rotation for one in the input rot matrix.
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

            obj_evaluated = obj.evaluated_get(depsgraph)  #modifiers need to be applied before taking any info from them such as coordinates. .co does not include modifiers.

            if obj.parent:
                init_parent = obj.parent
            else:
                init_parent = None

            init_children = obj.children
            attribute = obj_evaluated.data.attributes.get(self.src_attr_name)

            if attribute == None:
                message = f'Attribute {self.src_attr_name} not found on {obj.name}. Skipping.'
                self.report({'INFO'}, message)
                continue

            attr_info = {}
            
            for index,data in enumerate(attribute.data): #CREATE DICTIONARY
                
                if int(data.vector[1]) == 0 or int(data.vector[1] <= 999): #Check attribute format. If attribute value is 0 set it to default 1111
                    data.vector[1] = 1111.0



                # ------------ Create dictionary where vertex index is picked based on its attribute value. ------------

                #X Channel of vector attribute
                attr_val_x = int(data.vector[0])                    #Mesh ID

                #Y channel of vector attribute.1111 format. 1 = False, 2 = True
                attr_val_y_1 = int(data.vector[1] % 10)             #Z Axis Direction   (Get Ones)      
                attr_val_y_2 = int(data.vector[1] // 10 % 10)       #Y Axis Direction   (Get Tens) 
                attr_val_y_3 = int(data.vector[1] // 100 % 10)      #X Axis Direction   (Get Hundreds)  
                attr_val_y_4 = int(data.vector[1] // 1000 % 10)     #Pivot Position     (Get Thousands) 

                #Z Channel of vector attribute
                i_val_z = int(data.vector[2])                       #Parent Mesh ID


                if attr_val_x not in attr_info: #Create new if mesh ID not present already
                    attr_info[attr_val_x] = {
                        'index': [],
                        'pivot_index': [],
                        'x_axis_index': [],
                        'y_axis_index': [],
                        'z_axis_index': [], #(Optional)
                        'parent_element_id': None,
                        'object':None
                    }

                attr_info[attr_val_x]['index'].append(index)

                attr_info[attr_val_x]['parent_element_id'] = i_val_z

                if attr_val_y_4 == 2:
                    # sub_element_len += 1
                    attr_info[attr_val_x]['pivot_index'].append(index) #Vertex index that belongs to Pivot. Find: vertex[index].co
                    # attr_info[i_val_int]['parent_element_id'] = int(100*(round(i_val*10%1,2))) #This number points to a key in this dictionary. (Parent obj).

                if attr_val_y_3 == 2:
                    attr_info[attr_val_x]['x_axis_index'].append(index) #Vertex index where x axis points to.

                if attr_val_y_2 == 2:
                    attr_info[attr_val_x]['y_axis_index'].append(index) #Vertex index where Y axis points to.

                if attr_val_y_1 == 2:
                    attr_info[attr_val_x]['z_axis_index'].append(index) #Vertex index where Z axis points to.

            attr_info_ordered = OrderedDict(sorted(attr_info.items(), key=lambda x: x[0]))


            # print(f'{attr_info_ordered= }')
            for idx in attr_info_ordered: #idx is int, idx is one mesh element. 


                # ------------------ GET ORIGIN LOCAL AND GLOBAL POSITION FROM VERTEX INDEXES + AVERAGED VERSION ------------------
                origin_position_global_avg, origin_position_local_avg, normal_vector_local = position_from_loop_indices(obj_evaluated,attr_info_ordered[idx]['pivot_index'])


                # ------------------ ORIGIN ROTATION GET ------------------
                # ------ Get Directional Vector X from  vertex positions + averaged version ------
                directional_vector_x = directional_vector_from_loop_indices(obj_evaluated,attr_info_ordered[idx]['x_axis_index'],origin_position_local_avg)


                # ------ Get Directional Vector Y  ------
                directional_vector_y = directional_vector_from_loop_indices(obj_evaluated,attr_info_ordered[idx]['y_axis_index'],origin_position_local_avg)


                # ------ Get Directional Vector Z  ------
                directional_vector_z = directional_vector_from_loop_indices(obj_evaluated,attr_info_ordered[idx]['z_axis_index'],origin_position_local_avg)




                #Get rotational matrix from directional vectors
                
                #If All X, Y, Z provided,
                if directional_vector_x and directional_vector_y and directional_vector_z:
                    orthagonal_xyz_axis =gram_schmidt_orthogonalization(directional_vector_x, directional_vector_y, directional_vector_z)
    
                    #Rotational matrix from orthagonal axis vectors
                    rotational_matrix = vec_to_rotational_matrix(orthagonal_xyz_axis[0],orthagonal_xyz_axis[1],orthagonal_xyz_axis[2])
                    print("All is provided")


                #If only Z and Y provided (Take X from cross product)
                elif directional_vector_y and directional_vector_z and not directional_vector_x:

                    directional_vector_x = directional_vector_y.cross(directional_vector_z) #Result is right handed coord system

                    orthagonal_xyz_axis = gram_schmidt_orthogonalization(directional_vector_x, directional_vector_y, directional_vector_z)
                    rotational_matrix = vec_to_rotational_matrix(orthagonal_xyz_axis[0],orthagonal_xyz_axis[1],orthagonal_xyz_axis[2])
                    print("Calculating X")

                #If only Y and X provided (Take Z from normal)
                elif directional_vector_z == None and len(attr_info_ordered[idx]['pivot_index']) > 0: #If Z isnt provided origin normal is used.
                    directional_vector_z = normal_vector_local @ obj_evaluated.matrix_world.inverted()
                    directional_vector_z = directional_vector_z.normalized()

                    orthagonal_xyz_axis =gram_schmidt_orthogonalization(directional_vector_x, directional_vector_y, directional_vector_z)
    
                    #Rotational matrix from orthagonal axis vectors
                    rotational_matrix = vec_to_rotational_matrix(orthagonal_xyz_axis[0],orthagonal_xyz_axis[1],orthagonal_xyz_axis[2])
                    print("Calculating Z")


                #If only X and Z provided (Take Y fom cross product)
                elif directional_vector_x and directional_vector_z and not directional_vector_y:

                    directional_vector_y = directional_vector_z.cross(directional_vector_x) #Result is right handed coord system

                    orthagonal_xyz_axis = gram_schmidt_orthogonalization(directional_vector_x, directional_vector_y, directional_vector_z)
                    rotational_matrix = vec_to_rotational_matrix(orthagonal_xyz_axis[0],orthagonal_xyz_axis[1],orthagonal_xyz_axis[2])
                    print("Calculating Y")
                else:
                    rotational_matrix = None



                #Fix left handed coord system to right handed (Blender). Othervise mesh scale is negated.
                if self.fix_left_handed_axis:
                    right = is_right_handed(orthagonal_xyz_axis[0], orthagonal_xyz_axis[1], orthagonal_xyz_axis[2]) #Check if is right hand coord system
                    if right == False:
                        orthagonal_xyz_axis[1].negate() #Currently flipping Y axis but could be any axis



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
                loops_to_verts = list(set([element.data.vertices[element.data.loops[loop].vertex_index].index for loop in attr_info_ordered[idx]['index']]))

                lr_functions.delete_verts(element,loops_to_verts,invert=True)

                attr_info_ordered[idx]['object'] = element #Assign detached object to dictionary


                # ------------ SET ORIGIN POSITION ------------
                if origin_position_global_avg:
                    
                    move_origin_to_coord(element,
                                         origin_position_global_avg[0],
                                         origin_position_global_avg[1],
                                         origin_position_global_avg[2])

                # ------------ SET ORIGIN ROTATION ------------

                if rotational_matrix:
                    set_origin_rotation(element,rotational_matrix.to_4x4())


            # ------------  SELECT ALL, MAKE ID0 ACTIVE AND PARENT  ------------

            for idx in attr_info_ordered:
                if attr_info_ordered[idx]['object']:
                    attr_info_ordered[idx]['object'].select_set(True)
                    if idx == 0 or attr_info_ordered[idx]['parent_element_id'] == 0.0:
                        bpy.context.view_layer.objects.active = attr_info_ordered[idx]['object']
                        
                        if init_parent != None: #Set Index 0 as a child of the original parent.
                            parent_objects(attr_info_ordered[idx]['object'],init_parent)

                    if attr_info_ordered[idx]['parent_element_id'] != 0.0: 

                        if attr_info_ordered[idx]['parent_element_id'] != idx:
                            parent_id = attr_info_ordered[idx]['parent_element_id']
                            parent_objects(attr_info_ordered[idx]['object'], attr_info_ordered[parent_id]['object']) 
                    
                    if idx == 0:
                        if init_children:
                            for init_child in init_children:
                                parent_objects(init_child,attr_info_ordered[idx]['object'])

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

    target_attr_name: bpy.props.StringProperty(
        name="Target Attribute",
        description="Attribute name to store the data into",
        default='ObjInfo',
    )

    @classmethod
    def poll(cls, context): 
        return context.mode == 'OBJECT' or context.mode == 'EDIT_MESH'
        
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        selected_objects = bpy.context.selected_objects
        selected_objects.remove(bpy.context.active_object)
        selected_objects.insert(0,bpy.context.active_object) #Make sure active object is first in the list

        for index,obj in enumerate(selected_objects):
            for attribute in obj.data.attributes.active.data:
                attribute.vector[0] = index

        return {'FINISHED'}



class OBJECT_OT_lr_uv_offset_by_object(bpy.types.Operator):
    '''On Active attribute\nMultiple object selection. Active int attributes will be incremented on vertex domain per object. Decimal values stay unchanged.\nActive object gets 0'''
    bl_idname = "geometry.lr_set_per_obj_attribute"
    bl_label = "Increments int attribute on vertex domain"
    bl_options = {'REGISTER', 'UNDO'}

    target_attr_name: bpy.props.StringProperty(
        name="Target Attribute",
        description="Attribute name to store the data into",
        default='ObjInfo',
    )

    @classmethod
    def poll(cls, context): 
        return context.mode == 'OBJECT' or context.mode == 'EDIT_MESH'
        
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        def move_UVs(obj, u_offset, v_offset):
        
            if obj.type ==  'MESH': 
                uv_layer = obj.data.uv_layers.active.data
                for loop in obj.data.loops:
                    uv_coords = uv_layer[loop.index].uv
                    uv_coords[0] += u_offset
                    uv_coords[1] += v_offset

        for id,obj in enumerate(bpy.context.selected_objects):
            move_UVs(obj,0,id)

        return {'FINISHED'}


class OBJECT_OT_lr_obj_info_id_by_uv_island(bpy.types.Operator):
    '''Multiple or single object selection. based on V value in UV coordinate space. E.g. Vert: (U:0.122 V: 14.455), gets mesh element value of 14.\nScript goes through loops that belongs to a vertex averages its uv space and assigns the value to attribute on vertex domain'''
    bl_idname = "geometry.lr_obj_info_id_per_uv"
    bl_label = "Increments int attribute on vertex domain"
    bl_options = {'REGISTER', 'UNDO'}

    source_uv_attr_name: bpy.props.StringProperty(
        name="Source UV Attribute",
        description="Name of the UV attribute to take the info from",
        default='UVMap',
    )
    target_attr_name: bpy.props.StringProperty(
        name="Target Attribute",
        description="Attribute name to store the data into",
        default='ObjInfo',
    )
 
    @classmethod
    def poll(cls, context): 
        return context.mode == 'OBJECT'

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        selected_objects = bpy.context.selected_objects
        selected_objects.remove(bpy.context.active_object)
        selected_objects.insert(0,bpy.context.active_object) #Make sure active object is first in the list

        for obj in selected_objects:

            attr_target = obj.data.attributes.get(self.target_attr_name)  

            if attr_target == None:
                attr_target = obj.data.attributes.new(self.target_attr_name,'FLOAT_VECTOR', 'CORNER')
            
            elif attr_target.data_type != 'FLOAT_VECTOR' or attr_target.domain != 'CORNER':
                attr_target.name = self.target_attr_name+'_Backup'
                attr_target = obj.data.attributes.new(self.target_attr_name,'FLOAT_VECTOR', 'CORNER')


            uv_layer = obj.data.uv_layers.get(self.source_uv_attr_name)
            if uv_layer == None:
                self.report({'INFO'}, f'Missing attribute: {self.source_uv_attr_name} on: {obj.name} object.')
                continue          

            for loop in obj.data.loops:
                attr_target.data[loop.index].vector[0] = int(uv_layer.data[loop.index].uv[1])

        return {'FINISHED'}



class OBJECT_OT_lr_attribute_increment_values_mesh(bpy.types.Operator):
    '''On Active attribute\nMultiple object selection. Active int attributes will be incremented on vertex domain per mesh.\nActive object gets 0'''
    bl_idname = "geometry.lr_set_per_mesh_island_attribute"
    bl_label = "Increments int attribute on vertex domain"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context): 
        return context.mode == 'OBJECT' or context.mode == 'EDIT_MESH'

    attr_name: bpy.props.StringProperty(
        name="Source Attribute",
        description="Attribute with stored obj info data",
        default='ObjInfo',
    )
    # def invoke(self, context, event):
    #     wm = context.window_manager
    #     return wm.invoke_props_dialog(self)


    def execute(self, context):
        selected_objects = bpy.context.selected_objects
        selected_objects.remove(bpy.context.active_object)
        selected_objects.insert(0,bpy.context.active_object) #Make sure active object is first in the list
        objects_eval = {}

        for index,obj in enumerate(selected_objects):
            obj_index = objects_eval.get('index')
            if obj_index is None:
                objects_eval[index] = {}
                objects_eval[index]['elements_vert_indexes'] = None
                objects_eval[index]['object'] = None

            objects_eval[index]['elements_vert_indexes'] = lr_functions.get_vertex_islands(obj)
            objects_eval[index]['object'] = obj


        element_id = 0
        for obj_index in objects_eval:
            bm = bmesh.new()
            bm.from_mesh(objects_eval[obj_index]['object'].data)
            bm_layer = bm.loops.layers.float_vector.get(self.attr_name)
            if bm_layer == None:
                bm_layer = bm.loops.layers.float_vector.new(self.attr_name)


            for element in objects_eval[obj_index]['elements_vert_indexes']:
                for vert_id in element:
                    bm.verts.ensure_lookup_table()
                    for loop in bm.verts[vert_id].link_loops:
                        loop[bm_layer][0] = element_id
                element_id +=1

            bm.to_mesh(objects_eval[obj_index]['object'].data)
            bm.free()     


        return {'FINISHED'}
