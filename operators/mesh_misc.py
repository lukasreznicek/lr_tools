import bpy, bmesh, os,re,time
from mathutils import Vector, Matrix
from ..utils import lr_functions
from collections import defaultdict
from collections import OrderedDict


class MESH_OT_getEdgesLength(bpy.types.Operator):
    bl_idname = "mesh.lr_get_edges_length"
    bl_label = "Outputs length of selected edges"
    bl_options = {'REGISTER', 'UNDO'}

    edges_length: bpy.props.FloatProperty(name="Length: ",unit='LENGTH',precision=5)
    
    def execute(self, context):

        #Execute only if selection is mesh
        if len(bpy.context.selected_objects) != 0:
            if bpy.context.active_object.type == 'MESH':      
                
                
                bm = bmesh.from_edit_mesh(bpy.context.active_object.data)

                def sel_edges_length(bm):
                    length: float = 0
                    for edge in bm.edges:
                        if edge.select == True:
                            length += edge.calc_length()
                    return length

                #Default is meters
                length = sel_edges_length(bm)


                self.edges_length = length

        else:
            self.report({'ERROR'}, "Select object.")
            return {'FINISHED'}


        #self.report({'INFO'}, "Length: " + str(length))
        return {'FINISHED'}	    



class OBJECT_OT_hide_by_name(bpy.types.Operator):
    bl_idname = "object.lr_hide_object"
    bl_label = "Hides/Unhides object by name"
    bl_options = {'REGISTER', 'UNDO'}


    name: bpy.props.StringProperty(name="Name: ", default="UCX_",description = 'Hide objects containing')
    hide: bpy.props.BoolProperty(name = 'Hide',default = True)
        # @classmethod
        # def poll(cls, context): 
        # 	return context.mode == 'OBJECT'
            
    def execute(self, context):
        num = 0
        for i in bpy.context.view_layer.objects:
            if self.name in i.name:
                i.hide_viewport = self.hide
                num += 1


        self.report({'INFO'}, f'Updated {num} objects.')
        return {'FINISHED'}		



class OBJECT_OT_hide_wire_objects(bpy.types.Operator):
    bl_idname = "object.lr_hide_wire_object"
    bl_label = "Hides/Unhides objects with wire display mode"
    bl_options = {'REGISTER', 'UNDO'}
    '''Hides/Unhides objects with wire display mode'''

    hide_wire: bpy.props.BoolProperty(name = 'Hide',default = True)
        # @classmethod
        # def poll(cls, context): 
        # 	return context.mode == 'OBJECT'
            
    def execute(self, context):
        num = 0
        for i in bpy.context.view_layer.objects:
            if i.display_type == 'WIRE':
                i.hide_set(self.hide_wire)
                num += 1


        self.report({'INFO'}, f'Updated {num} objects.')
        return {'FINISHED'}		



class OBJECT_OT_hide_subsurf_modifier(bpy.types.Operator):
    bl_idname = "object.lr_hide_subd_modifier"
    bl_label = "Hides/Unhides subd modifier on selected objects."
    bl_options = {'REGISTER', 'UNDO'}

    hide_subsurf: bpy.props.BoolProperty(name="Hide SubD", default= False)
    hide_subsurf_active: bpy.props.BoolProperty(name="On Active", default= False)    
    def execute(self, context):
        
        for obj in bpy.context.selected_objects:
            for modifier in obj.modifiers:
                if modifier.type == 'SUBSURF':
                    
                    if self.hide_subsurf_active == True:
                        if modifier.is_active == True:
                            modifier.show_viewport = not self.hide_subsurf
                    else:
                        modifier.show_viewport = not self.hide_subsurf

        return {'FINISHED'}	    



class OBJECT_OT_lr_set_collection_offset_from_empty(bpy.types.Operator):
    '''Checks for empty with no parent inside collection and copies its position. Works on selected collections only'''
    bl_idname = "object.lr_set_collection_offset_from_empty"
    bl_label = "Checks for empty with no parent inside collection and copies its position. Works on selected collections only"
    bl_options = {'REGISTER', 'UNDO'}

    # @classmethod
    # def poll(cls, context): 
    # 	return context.mode == 'OBJECT'

    def execute(self, context):
        # outliner_selection = lr_functions.get_outliner_selection()
        
        # for selection in outliner_selection:

        #     for object in selection.objects:
        #         if ((object.type == 'EMPTY') and (object.parent == None)):
        #             selection.instance_offset = object.location
                    
        for obj in bpy.context.selected_objects:
            for coll in obj.users_collection:
                coll.instance_offset = obj.location



        return {'FINISHED'}		



class OBJECT_OT_material_slot_remove_unused_on_selected(bpy.types.Operator):
    '''Removes unused material slots on all selected objects. Same as blender default operator but works with multiple object selection'''
    bl_idname = "object.material_slot_remove_unused_on_selected"
    bl_label = "Same as blender default operator but works with multiple object selection."
    bl_options = {'REGISTER', 'UNDO'}

    # @classmethod
    # def poll(cls, context): 
    # 	return context.mode == 'OBJECT'

    def execute(self, context):
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                bpy.ops.object.material_slot_remove_unused()
        return {'FINISHED'}		



class OBJECT_OT_lr_material_cleanup(bpy.types.Operator):
    '''Checks materials for suffixes and assings the lowest material or material without suffix. Intended for removing duplicated materials. Only on selected objects'''
    bl_idname = "object.lr_material_cleanup"
    bl_label = "Checks materials for suffixes and assings the lowest material or material without suffix."
    bl_options = {'REGISTER', 'UNDO'}

    # @classmethod
    # def poll(cls, context): 
    # 	return context.mode == 'OBJECT'

    def execute(self, context):
        src_materials = []
        for src_material in bpy.data.materials:
            src_materials.append(src_material)

        selected_objects = []

        for object in bpy.context.selected_objects:
            if object.type == 'MESH':
                selected_objects.append(object)                            #Will add every instance in case of material assignment to object and not data.
            
        for object in selected_objects:
            for obj_material in object.material_slots:
                if obj_material.name != '':                                     #Empty material slot check
                    res = re.split('(\.\d+$)', obj_material.material.name)
                    if len(res) > 1:
                        matches = []
                        for src_material in src_materials:
                            if re.search(res[0], src_material.name):
                                matches.append(src_material)
                        obj_material.material = matches[0]


        return {'FINISHED'}		



class OBJECT_OT_view_object_rotate(bpy.types.Operator):
    bl_idname = "object.view_object_rotate"
    bl_label = "Rotates object 90° based on viewport position"
    bl_options = {'REGISTER', 'UNDO'}
    
    view_rotate_left: bpy.props.BoolProperty(name="Left", default= False,options={'SKIP_SAVE'})    


    def execute(self, context):
        
        axis = lr_functions.get_view_orientation()

        #Rotate to Right
        if self.view_rotate_left == False:
            #FRONT, LEFT, BOTTOM
            if axis[1] == True:
                bpy.ops.transform.rotate(value=1.5708, constraint_axis=(axis[0][0], axis[0][1], axis[0][2]))
            #BACK, RIGHT, TOP
            if axis[1] == False:
                bpy.ops.transform.rotate(value=-1.5708, constraint_axis=(axis[0][0], axis[0][1], axis[0][2]))


        #Rotate to left
        if self.view_rotate_left == True:
            #FRONT, LEFT, BOTTOM
            if axis[1] == True:
                bpy.ops.transform.rotate(value=-1.5708, constraint_axis=(axis[0][0], axis[0][1], axis[0][2]))
            #BACK, RIGHT, TOP
            if axis[1] == False:
                bpy.ops.transform.rotate(value=1.5708, constraint_axis=(axis[0][0], axis[0][1], axis[0][2]))

            
                    
        return {'FINISHED'}



class OBJECT_OT_lr_assign_checker(bpy.types.Operator):
    bl_idname = "object.lr_assign_checker"
    bl_label = "Assigns checker texture"
    bl_options = {'REGISTER', 'UNDO'}
    
    
    def execute(self, context): 

        script_folder = bpy.utils.script_paths()
        script_folder.reverse()
        texture_path = None

        texture_name = 'T_CheckerMap_A.png'
        # print(os.path.dirname(os.path.realpath(__file__)))


        #Find script folder with addon
        found = False
        for path in script_folder:
            path = os.path.join(path,'addons')
            if os.path.exists(path):
                if 'lr_tools' in os.listdir(path) or 'lr_tools-master' in os.listdir(path):
                    texture_full_path = os.path.join(path,'lr_tools','textures',texture_name)
                    found = True

        if found == False:
            message = 'Addon folder name in scripts directory should be: lr_tools. Please Rename.'
            self.report({'ERROR'}, message)
            return {'FINISHED'}
        
        #Load image
        bpy.data.images.load(texture_full_path, check_existing=True)
        
    
        #Create material function
        if 'MF_LR_Checker' not in bpy.data.node_groups:
            mf_lr_checker = bpy.data.node_groups.new('MF_LR_Checker','ShaderNodeTree')

            mf_lr_checker_input_socket = bpy.data.node_groups['MF_LR_Checker'].interface.items_tree.data.new_socket('ShaderInput',in_out='INPUT', socket_type= 'NodeSocketShader')
            mf_lr_checker_output_socket = bpy.data.node_groups['MF_LR_Checker'].interface.items_tree.data.new_socket('ShaderOutput',in_out='OUTPUT', socket_type= 'NodeSocketShader')


            tex_sample = bpy.data.node_groups['MF_LR_Checker'].nodes.new('ShaderNodeTexImage')  #Create texture node
            group_output = bpy.data.node_groups['MF_LR_Checker'].nodes.new('NodeGroupOutput')   #Create function output
            group_input = bpy.data.node_groups['MF_LR_Checker'].nodes.new('NodeGroupInput')     #Create function input
            #nodes = bpy.data.node_groups['LR_Checker'].nodes

            bpy.data.node_groups['MF_LR_Checker'].links.new(group_output.inputs[0],tex_sample.outputs[0])   #Link 
            tex_sample.image = bpy.data.images[texture_name]

        # #Exec

        #Go get materials on object         
        obj_materials = []
        for mslot in bpy.context.object.material_slots:
            obj_materials.append(mslot.material)
            

        #LR Material function
        for obj_material in obj_materials:

        

        #Output node
            material_output_check = False
            for node in obj_material.node_tree.nodes:
                #Find/declare output node and it's input
                

                if node.type == "OUTPUT_MATERIAL": 
                    material_output_check = True
                    node_output = node
                    
                    if len(node.inputs['Surface'].links) >= 1:
                        node_output_input_source = node.inputs['Surface'].links[0].from_socket

                        # print (f'{node_output_input_source = }')
                        node_output_input_node = node.inputs['Surface'].links[0].from_node
                        # print (f'{node_output_input_node = }')
                    else:
                        node_output_input_source = False



            #Create/declare output node if does not exist  
            if material_output_check == False:
                node_output = obj_material.node_tree.nodes.new("ShaderNodeOutputMaterial")
                node_output_input_source = False


            #Add MF into shader
            create = True
            if node_output_input_node.type == 'GROUP':
                if node_output_input_node.node_tree.name == 'MF_LR_Checker':
                    create = False
           
            if create == True:
                group = obj_material.node_tree.nodes.new('ShaderNodeGroup')
                group.name = 'LR_Checker' 
                group.node_tree = bpy.data.node_groups['MF_LR_Checker']


                #Relink to new node
                if node_output_input_source != False:
                    obj_material.node_tree.links.new(node_output_input_source, group.inputs[0])   
                obj_material.node_tree.links.new(group.outputs[0], node_output.inputs['Surface'])


        if texture_full_path == None:
            print('Could not find checker texture')
            return {'FINISHED'}
        else:
            pass

        return {'FINISHED'}



class OBJECT_OT_lr_remove_checker(bpy.types.Operator):
    bl_idname = "object.lr_remove_checker"
    bl_label = "Removes checker texture"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context): 

        obj_materials = []
        for mslot in bpy.context.object.material_slots:
            obj_materials.append(mslot.material)
        
        for obj_material in obj_materials:
            for node in obj_material.node_tree.nodes:
                if node.type == 'GROUP' and node.node_tree.name == 'MF_LR_Checker':
                    if len(node.inputs[0].links) >= 1:
                        obj_material.node_tree.links.new(node.inputs[0].links[0].from_socket,node.outputs[0].links[0].to_socket)
                    
                    obj_material.node_tree.nodes.remove(node)
        



        return {'FINISHED'}





#Slow Disabled
class OBJECT_OT_join_selection_and_parent(bpy.types.Operator):
    """For each selected object parent object is checked and meged with selection. Select only child, parent object is detected in script. Handles children reparenting"""
    bl_idname = "object.join_with_parent"
    bl_label = "Joins/merges current selection with its parent object"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):
        import bpy

        def set_parent(child, parent):
            child.parent = parent
            child.matrix_parent_inverse = parent.matrix_world.inverted()

        store_obj_sel = bpy.context.selected_objects
        store_active_sel_parent = bpy.context.view_layer.objects.active.parent
        bpy.ops.object.select_all(action='DESELECT')

        parent_objs = []

        for obj in store_obj_sel:

            if obj.parent:
                parent = obj.parent
                parent_objs.append(parent)
                obj.select_set(True)
                obj.parent.select_set(True)
                bpy.context.view_layer.objects.active = parent


                for child in obj.children:
                    set_parent(child,parent)

                bpy.ops.object.join()
                
                bpy.ops.object.select_all(action='DESELECT')
                
            
        #restore
        for obj in parent_objs:
            obj.select_set(True)

        bpy.context.view_layer.objects.active = store_active_sel_parent

            
                    
        return {'FINISHED'}
    

def set_parent(child, parent):
    mat_world = child.matrix_world
    child.parent = parent
    child.matrix_world = mat_world            
    

# def join_objects(obj1, obj2, deps_graph, remove_original_obj2 = True):
#     """Obj2 is added to Obj1"""
#     bm = bmesh.new()

#     bm.from_object(obj2,deps_graph)
#     bm.transform(obj2.matrix_world)
#     bm.transform(obj1.matrix_world.inverted())

#     bm.from_object(obj1,deps_graph)

#     bm.to_mesh(obj1.data)
#     if remove_original_obj2:
#         bpy.data.objects.remove(obj2)
def join_objects(obj1, obj2, remove_original_obj2 = True):
    """Obj2 is added to Obj1. Fast. Does not apply modifiers, takes a long time."""
    
    #--- Material IDs reassignment ---
    obj2_materials = obj2.data.materials.values() #Empty = None, othervise material
    obj2_polycount = len(obj2.data.polygons)
    obj2_mat_ids = [0]*obj2_polycount
    obj2_mat_ids_changed = list(obj2_mat_ids)

    obj2.data.polygons.foreach_get("material_index", obj2_mat_ids)
    obj1_materials = obj1.data.materials.values()
    material_pairs = [] #(obj2 mat index, obj1 mat index)
    for idx,material in enumerate(obj2_materials):
        if material in obj1_materials:
            material_pairs.append((idx,obj1_materials.index(material)))
        else:
            obj1.data.materials.append(material)
            obj1_materials.append(material) #If same materials in obj2 then merge them. Remove this line to keep same materials
            material_pairs.append((idx,len(obj1.data.materials)-1))


    if len(material_pairs) == 1:
        for idx in range(len(obj2_mat_ids)):
            obj2_mat_ids_changed[idx] = material_pairs[0][1]
    else:
        for idx in range(len(obj2_mat_ids)):
            for pair in material_pairs:
                if obj2_mat_ids[idx] == pair[0]:
                    obj2_mat_ids_changed[idx]=pair[1]

    obj2.data.polygons.foreach_set("material_index", obj2_mat_ids_changed)
    #--- End ---

    bm = bmesh.new()
    bm.from_mesh(obj2.data)


    bm.transform(obj2.matrix_world)
    bm.transform(obj1.matrix_world.inverted())

    bm.from_mesh(obj1.data)


    # for slot in obj1.material_slots:
    #     bm.faces.ensure_lookup_table()  # Ensure faces are ready
    #     for f in bm.faces:
    #         if f.material_index == slot.index:
    #             f.material_index = slot.index  # Assign the same material index

    bm.to_mesh(obj1.data)
    if remove_original_obj2:
        bpy.data.objects.remove(obj2)
    bm.free()
    
    
class OBJECT_OT_join_selection_and_parent_bmesh(bpy.types.Operator):
    """For each selected object parent object is checked and meged with selection. Select only child, parent object is detected in script. Handles children reparenting"""
    bl_idname = "object.join_with_parent_bmesh"
    bl_label = "Joins/merges current selection with its parent object"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):
        import bpy
        import bmesh
        import time
        s_time = time.time()
        store_obj_sel = bpy.context.selected_objects
        store_active_sel_parent = bpy.context.view_layer.objects.active.parent
        bpy.ops.object.select_all(action='DESELECT')

        
        parent_objs = []
        dg = bpy.context.evaluated_depsgraph_get()
        for obj in store_obj_sel:
            if obj.parent:
                parent_objs.append(obj.parent)
                for child in obj.children:

                    set_parent(child,obj.parent)
                
                join_objects(obj.parent, obj, remove_original_obj2 = False)

        for obj in store_obj_sel:
            bpy.data.objects.remove(obj)

        #restore
        for obj in parent_objs:
            obj.select_set(True)

        bpy.context.view_layer.objects.active = store_active_sel_parent
        elapsed_time = time.time() - s_time
        time = f"In: {elapsed_time:.3f}s"
        self.report({'INFO'}, time)
        return {'FINISHED'}



class OBJECT_OT_lr_rebuild(bpy.types.Operator):
    '''
    
    Breaks selected objects into subcomponent based on values in Elements attribute.
    
    Whole number = Subelement index, this list includes indexes mentioned below
    .1 = subelement pivot point.
    .2 = Subelement X axis.
    .3 = Subelement Y axis.
    ._01 = Second and third decimal is parent subelement index. If unspecified parent is index 0.
    '''


    bl_idname = "object.lr_rebuild"
    bl_label = "Breaks down mesh into subcomponents"
    bl_options = {'REGISTER', 'UNDO'}

    remove_extra: bpy.props.BoolProperty(
        name="Remove Extra",
        description="Remove vertices for pivot position. X axis and Y Axis",
        default=False,
    )


    # @classmethod
    # def poll(cls, context): 
    #     return context.mode == 'OBJECT' or context.mode == 'EDIT_MESH'
        
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

            


    def execute(self, context): 
        objs = bpy.context.selected_objects

        
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
        def get_global_vertex_position(obj, vertex_index):
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
            
            # Get the mesh data of the object
            mesh = obj.data
            
            # Ensure the vertex index is valid
            if vertex_index < 0 or vertex_index >= len(mesh.vertices):
                # print("Invalid vertex index.")
                return None
            
            # Access the vertex's local coordinates
            local_vertex_co = mesh.vertices[vertex_index].co
            
            # Get the global coordinates of the vertex
            global_vertex_co = obj.matrix_world @ local_vertex_co
            
            return global_vertex_co
        
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



        for obj in objs:

            obj.data = obj.data.copy() #Make object unique. Remove instancing.
            
            # print(f'{obj.data.users = }')

            act_obj = bpy.context.active_object
            bpy.context.view_layer.objects.active = obj
            for modifier in obj.modifiers: # Apply all modifier
                bpy.ops.object.modifier_apply(modifier=modifier.name)
            bpy.context.view_layer.objects.active = act_obj
            

            attr_name = 'Elements'

            if attr_name not in obj.data.attributes.keys():
                    message = f'Attribute {attr_name} not found on {obj.name}. Skipping.'
                    self.report({'INFO'}, message)
                    continue


            sub_elements_attr = None
            for attr in obj.data.attributes.values():
                if attr.name == attr_name:
                    sub_elements_attr = attr


            sub_elements_attr_data = sub_elements_attr.data.values()


            
            # 0  = Parent object, 
            # Whole number = subelement index, this list includes indexes mentioned below
            # .1 = subelement pivot point.
            # .2 = Subelement X axis.
            # .3 = Subelement Y axis.
            attr_info = {}
            sub_element_len = 0
            for index,data in enumerate(sub_elements_attr_data):
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

            # print(f'{attr_info_ordered= }')

            pivot_position = []
            elements = []
            for idx in attr_info_ordered:

                #ORIGIN POSITION GET
                if attr_info_ordered[idx]['pivot_index']:
                    pivot_position = get_global_vertex_position(obj, attr_info_ordered[idx]['pivot_index'][0])
                else:
                    pivot_position = None




                #--- ORIGIN ROTATION ---
                
                #Get Directional Vector X
                if attr_info_ordered[idx]['x_axis_index'] != []:
                    origin_idx = attr_info_ordered[idx]['pivot_index'][0]
                    x_axis_idx = attr_info_ordered[idx]['x_axis_index'][0]
                    attr_info_ordered[idx]['x_axis_index']
                    directional_vector_x = (obj.matrix_world @ obj.data.vertices[x_axis_idx].co) - (obj.matrix_world @ obj.data.vertices[origin_idx].co) 
                else:
                    self.report({'ERROR'}, "Missing X axis. _.2")

                #Get Directional Vector Y
                if attr_info_ordered[idx]['y_axis_index'] != []:
                    origin_idx = attr_info_ordered[idx]['pivot_index'][0]
                    y_axis_idx = attr_info_ordered[idx]['y_axis_index'][0]
                    attr_info_ordered[idx]['x_axis_index']
                    directional_vector_y = (obj.matrix_world @ obj.data.vertices[y_axis_idx].co) - (obj.matrix_world @ obj.data.vertices[origin_idx].co)                 
                else:
                    self.report({'ERROR'}, "Missing X axis. _.3")

                #Get Directional Vector Z
                if attr_info_ordered[idx]['pivot_index'] != []:
                    directional_vector_z = obj.data.vertices[attr_info_ordered[idx]['pivot_index'][0]].normal @ obj.matrix_world.inverted()
                    directional_vector_z = directional_vector_z.normalized()
                else:
                    self.report({'ERROR'}, "Missing pivot position. Vert _.1")

                orthagonal_xyz_axis =gram_schmidt_orthogonalization(directional_vector_x, directional_vector_y, directional_vector_z)
                
                #Rotational matrix from orthagonal axis vectors
                rotational_matrix = vec_to_rotational_matrix(orthagonal_xyz_axis[0],orthagonal_xyz_axis[1],orthagonal_xyz_axis[2])

                if self.remove_extra: #Remove verticies which belong to pivot point x axis and y axis. 
                    attr_info[idx]['index'].remove(attr_info[idx]['x_axis_index'][0])
                    attr_info[idx]['index'].remove(attr_info[idx]['y_axis_index'][0])
                    attr_info[idx]['index'].remove(attr_info[idx]['pivot_index'][0])


                # ------ DUPLICATE ELEMENT INICIES AND SET ORIGIN POSITION ------
                element = element_separate(obj, attr_info[idx]['index'], parent =None, origin_coords = pivot_position)  #Add object information into ordered dictionary
                element.name = obj.name + '_part' + '_'+str(idx)
                attr_info_ordered[idx]['object'] = element #Assign detached object to dictionary

                # ------ ORIGIN ROTATION SET ------
                set_origin_rotation(element,rotational_matrix.to_4x4())



            # ------ SELECT MAKE ID0 ACTIVE AND PARENT  ------
            for idx in attr_info_ordered:
                    
                attr_info_ordered[idx]['object'].select_set(True)
                if idx == 0:
                    bpy.context.view_layer.objects.active = attr_info_ordered[idx]['object']

                if attr_info_ordered[idx]['parent_element_id'] != None: 

                    if attr_info_ordered[idx]['parent_element_id'] != idx:
                        parent_id = attr_info_ordered[idx]['parent_element_id']
                        parent_objects(attr_info_ordered[idx]['object'], attr_info_ordered[parent_id]['object']) 



            # for element in attr_info_ordered:
            #     print(f'ATTRIBUTE INFO #{element}: \n{attr_info_ordered[element]}')

            for col in obj.users_collection:
                col.objects.unlink(obj)

            bpy.data.objects.remove(obj)
            


        return {'FINISHED'}

