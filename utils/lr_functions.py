import random, bmesh, bpy, math
from mathutils import Vector,Matrix

def deselect_all_faces(bm):
    '''Deselects all faces'''
    for i in bm.faces:
        i.select = False


def deselect_faces(faces):
    '''Deselect faces'''
    for face in faces:
        face.select = False


def get_outliner_selection():
    '''If multiple outliners then outputs the first created one'''
    for area in bpy.context.screen.areas:
        if area.type == 'OUTLINER':
            outliner_area = area 

    with bpy.context.temp_override(area = outliner_area):
        return bpy.context.selected_ids



def get_view_orientation() -> ((bool,bool,bool),bool):
    '''
    
    Libs: bpy, mathutils.Vector
    Returns viewport axis alignment. Viewport view orientation.
    Returns: ((Bool,Bool,Bool),Bool) = ((X,Y,Z)PositiveOrNegative)
    '''
    r3d = bpy.context.area.spaces.active.region_3d
    view_matrix = r3d.view_matrix
    x,y,z = view_matrix.to_3x3()
    x,y,z = r3d.view_rotation @ Vector((0.0, 0.0, -1.0))

    view_rotation = (x,y,z)
    view_rotation_abs = (abs(x),abs(y),abs(z))

    axis_of_highest_index = view_rotation_abs.index(max(view_rotation_abs))


    #Determine whether it's positive or negative axis:
    if view_rotation[axis_of_highest_index] >0:
        axis_positive = True
    else:
        axis_positive = False


    #X Axis
    if axis_of_highest_index == 0:
        if axis_positive == True:
            return ((True,False,False),True)
        else:
            return ((True,False,False),False)


    #Y Axis
    if axis_of_highest_index == 1:
        if axis_positive == True:
            return ((False,True,False),True)
        else:
            return ((False,True,False),False)


    #Z Axis
    if axis_of_highest_index == 2:
        if axis_positive == True:
            return ((False,False,True),True)
        else:
            return ((False,False,True),False)



def select_faces(faces):
    '''Select faces'''
    for face in faces:
        face.select = True


def deselect_all_loops(bm,uv_layer):
    '''Deselct all loops'''
    for i in bm.faces:
        for j in i.loops:
            j[uv_layer].select = False


def select_loops_on_faces(bm,faces_list,uv_layer):
    '''Select loops on faces'''
    for face in faces_list:
        for loop in face.loops:
            loop[uv_layer].select = True


def select_loops(loop_list, uv_layer):
    '''Selects loops in UV editor'''
    for loop in loop_list:
        loop[uv_layer].select = True


def get_flipped_uv_faces(bm, bm_faces, uv_layer=False):
    ''' Input list of bmfaces and return flipped faces in UV space.'''
    
    # Create BMesh from active object (e.g. selected one)
    #bm = bmesh.from_edit_mesh(active_object.data)
    if uv_layer == False:
        uv_layer = bm.loops.layers.uv.verify()
    
    flipped_faces =[]

    for face in bm.faces:
        sum_edges = 0
        # Only loop 3 verts ignore others: faster!
        for i in range(3):
            uv_A = face.loops[i][uv_layer].uv
            uv_B = face.loops[(i+1)%3][uv_layer].uv
            sum_edges += (uv_B.x - uv_A.x) * (uv_B.y + uv_A.y)
            
        if sum_edges > 0:
            flipped_faces.append(face)

    return flipped_faces       


def deselect_loops_on_faces(bm,faces_list,uv_layer):
    '''Deselect Loops on faces'''
    for face in faces_list:
        for loop in face.loops:
            loop[uv_layer].select = False


def get_loop_selection(bm,uv_layer):
    '''Get loop selection'''
    selected_loops = [j for i in bm.faces for j in i.loops if j[uv_layer].select == True]
    return selected_loops


def get_selected_uv_faces_from_loops(selected_loops: list,uv_layer):
    '''Returns a SET of faces.'''
    loops = set(selected_loops)
    uv_faces = set()
    for i in loops:
            uv_faces.add(i.face)

    to_remove_set = set()
    for face in uv_faces:
        
        temp = True
        for f_loop in face.loops:
            if f_loop[uv_layer].select == False:
               temp = False 
        if temp == False:
            to_remove_set.add(face)

    uv_faces.difference_update(to_remove_set)
    return uv_faces


def get_face_selection(bm):
    '''Store face selection'''
    selected_faces = (i for i in bm.faces if i.select == True)
    return selected_faces


def remove_overlapping_loops(island_loops: list):
    '''Input one list only'''
    vert_sel_ind = set()
    vert_sel = []
    for i in island_loops:
        if i.vert.index not in vert_sel_ind:
            vert_sel.append(i)
        vert_sel_ind.add(i.vert.index)
    return vert_sel


def get_list_of_loops_from_faces(faces: list,uv_layer):
    """Get list of loops from list of faces."""
    loops = []
    for face in faces:
        for loop in face.loops:
            loops.append(loop)       
    return loops


def get_list_of_selected_loops_from_faces(faces: list,uv_layer):
    sel_loops = []    
    """Get list of selected loops from list of faces."""

    for face in faces:
        temp = []
        temp_sel = set()
        for loop in face.loops:
            temp.append(loop)
            temp_sel.add(loop[uv_layer].select)

        if False not in temp_sel:
            sel_loops.extend(temp)
    return sel_loops


def get_faces_by_seam_islands(bm,obj_data):
    '''Returns a list with face islands.'''
    #Get all indexes
    all_not_hidden_faces = [i for i in bm.faces if i.hide == False]
    all_not_hidden_faces_set = set(all_not_hidden_faces)
    
    get_selected_faces = set()
    for i in all_not_hidden_faces_set:
        if i.select:
            get_selected_faces.add(i)

    island = [] 
    count = 0  
    
    while all_not_hidden_faces_set:
        #Deselect all faces
        for i in all_not_hidden_faces_set:
            i.select = False

        if count != 0:
            all_not_hidden_faces_set.difference_update(temp) 
        
        #Get random face
        if all_not_hidden_faces_set:
            rand_face = random.choice(tuple(all_not_hidden_faces_set))

        #Select random index
        rand_face.select = True
        bmesh.update_edit_mesh(obj_data)

        #Select linked faces from random index (fastest)
        bpy.ops.mesh.select_linked(delimit={'SEAM'})

        temp = set() 
        for i in all_not_hidden_faces_set:
            if i.select == True:
                temp.add(i)

        if all_not_hidden_faces_set:
            island.append(list(temp))
        count += 1
        
        
    for i in bm.faces:
        i.select = False

    for i in get_selected_faces:
        i.select = True
    bmesh.update_edit_mesh(obj_data)    
        
    return(island)


#def get_linked_loop


def uv_loops_length(sel_loops: list,uv_layer,aspect_correction=[1,1]):
    '''Input: List
        Output: List          
        List of lists is not supported
    '''
    def length_between_poi(uv1,uv2):
        uv1[0] *= aspect_correction[0]
        uv1[1] *= aspect_correction[1]
        uv2[0] *= aspect_correction[0]
        uv2[1] *= aspect_correction[1]
        
    
        distance = math.sqrt((math.pow((uv2[0]-uv1[0]), 2)) + (math.pow((uv2[1]-uv1[1]), 2)))
        return distance

    uvs = []
    edge_mem = []
    for i in sel_loops:
        f_uv = [i[uv_layer].uv[0],i[uv_layer].uv[1]]                                    #First loop
        s_uv = [i.link_loop_next[uv_layer].uv[0],i.link_loop_next[uv_layer].uv[1]]      #Second connected loop
        
        edge_index = i.edge.index
        uvs.append([edge_index,[f_uv,s_uv]])                                            #Selected uvs in uv editor         
        edge_mem.append(edge_index)


    #Calculate and append distance
    distance = []
    for k in uvs:
        leng = length_between_poi(k[1][0], k[1][1])
        distance.append(leng)
    
    
    return distance


def active_window():
    return bpy.context.region.id_data




# --- Function: get angle between local up axis and uv point ---
def cal_angle(midp,vert_loops,uv_layer,aspect_correction=[1,1]):

    angles = []
    for vert_loop in vert_loops:

    
        uvp = [vert_loop[uv_layer].uv[0]*aspect_correction[0],vert_loop[uv_layer].uv[1]*aspect_correction[1]]
        if uvp[0] != midp[0]:
            slope = math.degrees(math.atan((midp[1]-uvp[1])/(midp[0]-uvp[0])))

        if uvp[0] > midp[0] and uvp[1] > midp[1]:
            slopec = slope

        elif uvp[0] < midp[0] and uvp[1] > midp[1]:
            slopec = slope+180

        elif uvp[0] < midp[0] and uvp[1] < midp[1]:
            slopec = slope +180  

        elif uvp[0] > midp[0] and uvp[1] < midp[1]:
            slopec = slope + 360

        elif uvp[0] < midp[0] and uvp[1] == midp[1]:
            slopec = 180

        elif uvp[0] > midp[0] and uvp[1] == midp[1]:
            slopec = 0

        elif uvp[0] == midp[0] and uvp[1] < midp[1]:
            slopec = 270

        elif uvp[0] == midp[0] and uvp[1] > midp[1]:
            slopec = 90

        elif uvp[0] == midp[0] and uvp[1] == midp[1]:
            slopec = False

        angles.append(slopec)
            
    return angles

# --- UV IMAGE ---

def get_active_uv_editor_images():
    '''Returns list of active images in UV editors.'''
    active_window = bpy.context.region.id_data
    images_in_order = [area.spaces.active.image for area in active_window.areas if area.ui_type == 'UV' and area.spaces.active.image != None]
    return images_in_order


def set_uv_loop_positions(stored_uvs: list, loops: list, uv_layer):
    '''Sets UV position from a list. List of list not supported. '''
    for uv,loop in zip(stored_uvs, loops):
        loop[uv_layer].uv[0] = uv[0]
        loop[uv_layer].uv[1] = uv[1]   

def get_image_display_aspect(image):
    '''Input:(bpy.data.image). Returns list with two floats.[1.0,1.2]'''
    return [image.display_aspect[0],image.display_aspect[1]]

def get_image_resolution(image):
    '''Input:(bpy.data.image). Returns list with two int.[2048,512]'''
    return [image.size[0],image.size[1]]

def store_uv_areas_with_image():
    '''Returns list'''
    active_window = bpy.context.region.id_data
    areas_in_order = [area for area in active_window.areas if area.ui_type == 'UV' and area.spaces.active.image != None]
    return areas_in_order

def sets_image_display_aspect(image,aspect: list):
    '''(bpy.data.image) Input list of two floats. e.g: [1.0,1.2]'''
    image.display_aspect[0] = aspect[0]
    image.display_aspect[1] = aspect[1]

def set_image_display_aspect_ratio_from_resolution(image: list):
    '''Takes images (bpy.data.image) and sets its aspect ratio in UV image editor'''
    ratio = image.size[0]/image.size[1]
    image.display_aspect[1] * ratio
    return ratio

def assign_images_to_uv_areas(images,uv_areas):
    for i,j in zip(images,uv_areas):
        j.spaces.active.image = i
# ---



def store_uv(loops: list, uv_layer):
    '''Output: [[x,y],[x,y],[x,y],...]'''
    # xy = []
    # for loop in loops:
    #     xyo = loop[uv_layer].uv.to_tuple(5)
    #     xy.append(xyo)
    xy = [loop[uv_layer].uv.to_tuple(5) for loop in loops]
    return xy   


def faces_to_loops(BM_Faces):
    '''   '''
    loops =[]
    for face in BM_Faces:
        for loop in face.loops:
            loops.append(loop)
    return loops


#Get uv center for transformation

#Inout:  [loop1,loop2,loop3]
#Output: [x_avg,y_avg]



def isl_cent(loops_lst: list,uv_layer,aspect_correction=[1,1]):

    '''Returns X and Y average center of input loops.'''

    x = [x[uv_layer].uv[0]*aspect_correction[0] for x in loops_lst]
    y = [x[uv_layer].uv[1]*aspect_correction[1] for x in loops_lst]

    avg  = [sum(x)/len(x),sum(y)/len(y)]
    return avg






def duplicate_obj(obj:bpy.types.Object,
                  depsgraph = None,
                  name:str = None,
                  apply_modifiers:bool = True,
                  parent:bpy.types.Object = None,
                  same_transform:bool = True,)->bpy.types.Object:
    
    """
    Duplicate object using BMesh.

    :param obj: The original object to duplicate.
    :param name: The name for the duplicated object and its mesh data.
    :param apply_modifiers: Whether to apply modifiers from the original object.
                            If True, the duplicated object will include the effects of modifiers.
                            If False, the duplicated object will have the same mesh data as the original.
    :return: Returns the duplicated object in world zero in active scene and collection.

    """
    if name !=None:
        name = obj.name

    bm = bmesh.new()

    if apply_modifiers:
        if depsgraph == None:
            depsgraph = bpy.context.evaluated_depsgraph_get() 

        bm.from_mesh(obj.evaluated_get(depsgraph).to_mesh())
        # print(f'{len(bm.faces)= }')
    else:
        bm.from_mesh(obj.data)


    obj_data_new = bpy.data.meshes.new(name+'_data')
    bm.to_mesh(obj_data_new)

    obj_new = bpy.data.objects.new(name,obj_data_new)
    
 
    for material in obj.data.materials: #Assign materials.
        obj_new.data.materials.append(material)
    obj_new.active_material_index = obj.active_material_index
    
    
    if parent != None:
        obj_new.parent = parent

    obj_new.matrix_world = obj.matrix_world if same_transform else Matrix.identity(4)


    bpy.context.collection.objects.link(obj_new) #link to scene
    # obj.collection.objects.link(obj_new)
    bm.free()
    
    return obj_new



# ''' Its working it just does not preserve materials


# def duplicate_obj(obj:bpy.types.Object, 
#                   name:str = None, 
#                   apply_modifiers:bool = True,
#                   parent:bpy.types.Object = None,
#                   same_transform:bool = True)->bpy.types.Object:
    
#     """
#     Duplicate object using BMesh.

#     :param obj: The original object to duplicate.
#     :param name: The name for the duplicated object and its mesh data.
#     :param apply_modifiers: Whether to apply modifiers from the original object.
#                             If True, the duplicated object will include the effects of modifiers.
#                             If False, the duplicated object will have the same mesh data as the original.
#     :return: Returns the duplicated object in world zero in active scene and collection.

#     """
#     if name !=None:
#         name = obj.name

#     bm = bmesh.new()

#     if apply_modifiers:

#         depsgraph = bpy.context.evaluated_depsgraph_get() 
        
#         bm.from_mesh(obj.evaluated_get(depsgraph).data)


    
    
#     else:
#         bm.from_mesh(obj.data)


#     obj_data_new = bpy.data.meshes.new(name+'_data')
#     bm.to_mesh(obj_data_new)

#     obj_new = bpy.data.objects.new(name,obj_data_new)
    
    
#     if parent != None:
#         obj_new.parent = parent

#     if same_transform == True:
#         obj_new.matrix_world = obj.matrix_world
#     else:
#         obj_new.matrix_world = Matrix.identity(4)


#     bpy.context.collection.objects.link(obj_new) #link to scene
#     # obj.collection.objects.link(obj_new)
#     bm.free()
    
#     return obj_new
# # '''







# #Slowe then the upper one but Preseves 
# def duplicate_obj(obj:bpy.types.Object, 
#                   name:str = None, 
#                   apply_modifiers:bool = True,
#                   parent:bpy.types.Object = None,
#                   same_transform:bool = True)->bpy.types.Object:
    
#     """
#     Duplicate object using BMesh.

#     :param obj: The original object to duplicate.
#     :param name: The name for the duplicated object and its mesh data.
#     :param apply_modifiers: Whether to apply modifiers from the original object.
#                             If True, the duplicated object will include the effects of modifiers.
#                             If False, the duplicated object will have the same mesh data as the original.
#     :return: Returns the duplicated object in world zero in active scene and collection.

#     """
#     if name !=None:
#         name = obj.name

#     if apply_modifiers:
        
        
#         object_new = obj.copy()
#         object_new.data = obj.data.copy()

#         for collection in obj.users_collection: 
#             collection.objects.link(object_new)
            
#         #SHIT/SLOW VERSION, Other version get gepsgraph + obj.modifiers.clear() was crashing blender
#         if object_new.modifiers.keys() != []:  
#             act_obj= bpy.context.active_object
#             bpy.context.view_layer.objects.active = object_new
#             for modifier in obj.modifiers: # Apply all modifier
#                 bpy.ops.object.modifier_apply(modifier=modifier.name, single_user=True)
#             bpy.context.view_layer.objects.active = act_obj


#     else:
#         object_new = obj.copy()
#         object_new.data = obj.data.copy()

#         for collection in obj.users_collection: 
#             collection.objects.link(object_new)

            
#     if parent != None:
#         object_new.parent = parent

#     if same_transform == True:
#         object_new.matrix_world = obj.matrix_world
#     else:
#         object_new.matrix_world = Matrix.identity(4)


#     # bpy.context.collection.objects.link(object_new) #link to scene



#     return object_new














def delete_verts(obj:bpy.types.Object,
                 vertices:list,
                 invert:bool = False):
    '''
    :param vertices_to_keep: list of vertex indexes. [1,54,68,78,2,33...]
    :param invert: 
    '''
    if bpy.context.mode == 'EDIT_MESH':
        bm = bmesh.from_edit_mesh(obj.data)
    if bpy.context.mode == 'OBJECT':
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        
    if invert == True:
        vertices_to_delete = [v for v in bm.verts if v.index not in vertices]
    else:
        vertices_to_delete = [v for v in bm.verts if v.index in vertices]
    
    bmesh.ops.delete(bm, geom=vertices_to_delete, context='VERTS')
    
    
    if bpy.context.mode == 'EDIT_MESH':
        bmesh.update_edit_mesh(obj.data)
    if bpy.context.mode == 'OBJECT':
        bm.to_mesh(obj.data)
        obj.data.update()




# def vector_average_position(vectors:list):
#     """
#     Calculate the average position of a list of vectors.
    
#     Parameters:
#         vectors (list of mathutils.Vector): List of vectors.

#     Returns:
#         mathutils.Vector: Average position vector.
#     """
#     # Check if the list is not empty
#     if not vectors:
#         raise ValueError("Input list of vectors is empty.")

#     # Initialize a Vector with zeros
#     average_vector = Vector((0.0, 0.0, 0.0))

#     # Calculate the sum of vectors
#     for vector in vectors:
#         average_vector += vector

#     # Divide by the number of vectors to get the average
#     average_vector /= len(vectors)

#     return average_vector