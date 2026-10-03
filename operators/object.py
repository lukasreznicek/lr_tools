import bpy, bmesh, os, re, time
from mathutils import Vector, Matrix
from ..utils import lr_functions
from collections import defaultdict
from collections import OrderedDict
from .. import config
from math import degrees
from bpy.props import BoolProperty


class OBJECT_OT_lr_origin_to_selection(bpy.types.Operator):
    bl_idname = "object.lr_origin_to_selection"
    bl_label = "Origin to Selection"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        cursor = context.scene.cursor
        stored_cursor_location = cursor.location.copy()

        active_object = context.active_object
        
        if active_object.mode == 'OBJECT':
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.view3d.snap_cursor_to_selected()
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')


        elif active_object.mode == 'EDIT':
            bpy.ops.view3d.snap_cursor_to_selected()
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
            bpy.ops.object.mode_set(mode='EDIT')

        cursor.location = stored_cursor_location

        self.report({'INFO'}, 'Origin set.')
        return {'FINISHED'}
    

def flatten(obj, depsgraph=None):
    if not depsgraph:
        depsgraph = bpy.context.evaluated_depsgraph_get()

    oldmesh = obj.data
    obj.data = bpy.data.meshes.new_from_object(obj.evaluated_get(depsgraph))
    obj.modifiers.clear()

    bpy.data.meshes.remove(oldmesh, do_unlink=True)

def unhide_deselect(mesh):
    polygons = len(mesh.polygons)
    edges = len(mesh.edges)
    vertices = len(mesh.vertices)

    mesh.polygons.foreach_set('hide', [False] * polygons)
    mesh.edges.foreach_set('hide', [False] * edges)
    mesh.vertices.foreach_set('hide', [False] * vertices)

    mesh.polygons.foreach_set('select', [False] * polygons)
    mesh.edges.foreach_set('select', [False] * edges)
    mesh.vertices.foreach_set('select', [False] * vertices)
    mesh.update()

def popup_message(message, title="Info", icon="INFO", terminal=True):
    def draw_message(self, context):
        if isinstance(message, list):
            for m in message:
                self.layout.label(text=m)
        else:
            self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw_message, title=title, icon=icon)

    if terminal:
        if icon == "FILE_TICK":
            icon = "ENABLE"
        elif icon == "CANCEL":
            icon = "DISABLE"
        print(icon, title)

        if isinstance(message, list):
            print(" »", ", ".join(message))
        else:
            print(" »", message)

def join(target, objects, select=[]):
    mxi = target.matrix_world.inverted_safe()

    bm = bmesh.new()
    bm.from_mesh(target.data)
    bm.normal_update()
    bm.verts.ensure_lookup_table()

    select_layer = bm.faces.layers.int.get('Machin3FaceSelect')

    if not select_layer:
        select_layer = bm.faces.layers.int.new('Machin3FaceSelect')

    for idx, obj in enumerate(objects):
        mesh = obj.data
        mx = obj.matrix_world
        mesh.transform(mxi @ mx)

        bmm = bmesh.new()
        bmm.from_mesh(mesh)
        bmm.normal_update()
        bmm.verts.ensure_lookup_table()

        obj_select_layer = bmm.faces.layers.int.get('Machin3FaceSelect')

        if not obj_select_layer:
            obj_select_layer = bmm.faces.layers.int.new('Machin3FaceSelect')

        for f in bmm.faces:
            f[obj_select_layer] = idx + 1

        bmm.to_mesh(mesh)
        bmm.free()

        bm.from_mesh(mesh)

        bpy.data.meshes.remove(mesh, do_unlink=True)

    if select:
        for f in bm.faces:
            if f[select_layer] in select:
                f.select_set(True)

    bm.to_mesh(target.data)
    bm.free()

class OBJECT_OT_lr_MeshCut(bpy.types.Operator):
    bl_idname = "object.mesh_cut"
    bl_label = "LR: Mesh Cut"
    bl_description = "Cut a Mesh Object, using another Object.\nALT: Flatten Target Object's Modifier Stack\nSHIFT: Mark Seams"
    bl_options = {'REGISTER', 'UNDO'}

    flatten_target: BoolProperty(name="Flatte Target's Modifier Stack", default=False)
    mark_seams: BoolProperty(name="Mark Seams", default=False)
    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT':
            return context.active_object and context.active_object.type == 'MESH'

    def draw(self, context):
        layout = self.layout
        column = layout.column()

        row = column.row(align=True)
        row.prop(self, 'flatten_target', text="Flatten Target", toggle=True)
        row.prop(self, 'mark_seams', toggle=True)

    def invoke(self, context, event):
        self.flatten_target = event.alt
        self.mark_seams = event.shift
        return self.execute(context)

    def execute(self, context):
        target = context.active_object
        cutters = [obj for obj in context.selected_objects if obj != target]

        if cutters:
            cutter = cutters[0]

            unhide_deselect(target.data)
            unhide_deselect(cutter.data)

            dg = context.evaluated_depsgraph_get()

            flatten(cutter, dg)

            if self.flatten_target:
                flatten(target, dg)

            cutter.data.materials.clear()

            join(target, [cutter], select=[1])

            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.intersect(separate_mode='ALL')
            bpy.ops.object.mode_set(mode='OBJECT')

            bm = bmesh.new()
            bm.from_mesh(target.data)
            bm.normal_update()
            bm.verts.ensure_lookup_table()

            select_layer = bm.faces.layers.int.get('Machin3FaceSelect')
            meshcut_layer = bm.edges.layers.int.get('Machin3EdgeMeshCut')

            if not meshcut_layer:
                meshcut_layer = bm.edges.layers.int.new('Machin3EdgeMeshCut')

            cutter_faces = [f for f in bm.faces if f[select_layer] > 0]
            bmesh.ops.delete(bm, geom=cutter_faces, context='FACES')

            non_manifold = [e for e in bm.edges if not e.is_manifold]

            verts = set()

            for e in non_manifold:
                e[meshcut_layer] = 1

                if self.mark_seams:
                    e.seam = True

                verts.update(e.verts)

            bmesh.ops.remove_doubles(bm, verts=list({v for e in non_manifold for v in e.verts}), dist=0.0001)

            straight_edged = []

            for v in verts:
                if v.is_valid and len(v.link_edges) == 2:
                    e1 = v.link_edges[0]
                    e2 = v.link_edges[1]

                    vector1 = e1.other_vert(v).co - v.co
                    vector2 = e2.other_vert(v).co - v.co

                    angle = degrees(vector1.angle(vector2))

                    if 179 <= angle <= 181:
                        straight_edged.append(v)

            bmesh.ops.dissolve_verts(bm, verts=straight_edged)

            bm.faces.layers.int.remove(select_layer)

            bm.to_mesh(target.data)
            bm.free()

            return {'FINISHED'}
        else:
            popup_message("Select one object first, then select the object to be cut last!", title="Illegal Sellection")
            return {'CANCELLED'}



class OBJECT_OT_lr_select_children_on_selected_objects(bpy.types.Operator):
    '''Adds all children to selection'''
    bl_idname = "object.lr_select_children_on_selected_objects"
    bl_label = "LR: Goes through objects and selects children"
    def execute(self, context):
        sel_obj = bpy.context.selected_objects

        for obj in sel_obj:
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.select_grouped(extend=True, type='CHILDREN_RECURSIVE')
        return {'FINISHED'}	   

class OBJECT_OT_lr_select_root_parent(bpy.types.Operator):
    bl_idname = "object.lr_select_root_parent"
    bl_label = "LR: Selects absolute parent"
    def execute(self, context):
        sel_obj = bpy.context.selected_objects
        
        bpy.ops.object.select_all(action='DESELECT')

        for obj in sel_obj:
            parent_obj = obj
            while parent_obj != None:
                top_parent = parent_obj
                parent_obj = parent_obj.parent

            top_parent.select_set(True)
            bpy.context.view_layer.objects.active = top_parent

        return {'FINISHED'}	    

class OBJECT_OT_select_bevel_object(bpy.types.Operator):
    """Select the bevel object of the active curve"""
    bl_idname = "object.select_bevel_object"
    bl_label = "LR: Select Bevel Object"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == 'CURVE' and obj.data.bevel_object is not None

    def execute(self, context):
        obj = context.active_object
        bevel_object = obj.data.bevel_object

        # Deselect everything
        bpy.ops.object.select_all(action='DESELECT')

        # Select bevel object
        bevel_object.select_set(True)
        context.view_layer.objects.active = bevel_object

        return {'FINISHED'}
    

    class OBJECT_OT_setup_uv_mask(bpy.types.Operator):
        """Creates and validates a 'UVMask' uv map and packs it"""
        bl_idname = "object.setup_uvmask"
        bl_label = "LR: Setup UV Mask"
        bl_options = {'REGISTER', 'UNDO'}

        # @classmethod
        # def poll(cls, context):
        #     obj = context.active_object
        #     return obj and obj.type == 'CURVE' and obj.data.bevel_object is not None

        def execute(self, context):
            
            #Preprocess
            process_objects = list(bpy.context.selected_objects)

            for obj in list(process_objects):
                if obj.name.startswith("UCX_"):
                    process_objects.remove(obj)
                if obj.type !="MESH":
                    process_objects.remove(obj)



            for obj in process_objects:

                if obj.type == 'MESH':
                    uvmap_name = "UVMask"
                    uvmaps = obj.data.uv_layers
                    if uvmap_name in uvmaps:
                        uvmaps.remove(uvmaps[uvmap_name])
                    
                    uvmaps.active = uvmaps['UVMap'] if 'UVMap' in uvmaps else uvmaps[0]
                    uvmap = uvmaps.new(name=uvmap_name)

                    # Set the UV map as active
                    uvmaps.active = uvmap

            bpy.ops.object.make_single_user(object=True, obdata=True, material=False, animation=False, obdata_animation=False)

            for obj in process_objects: 
                obj.select_set(True)    
            bpy.context.view_layer.objects.active = process_objects[0]
            # Pack UVs into 0-1 space
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.uv.select_all(action='SELECT')
            bpy.ops.uv.pack_islands(rotate=False, margin=0.001)
            bpy.ops.object.mode_set(mode='OBJECT')


            return {'FINISHED'}



class OBJECT_OT_lr_drop_object(bpy.types.Operator):
    """Drops object in Z Axis"""
    bl_idname = "lr.drop_object"
    bl_label = "Drops object in local or global Z axis."
    bl_options = {'REGISTER', 'UNDO'}

    #Property
    local_z_axis: bpy.props.BoolProperty(name = 'Local Z', description = 'Uses local Z axis instead of Global Z axis', default = True)
    rotate: bpy.props.BoolProperty(name = 'Match Rotation', description = 'Matches rotation to a mesh below', default = True)
    # @classmethod
    # def poll(cls, context):
    #     return context.mode == 'EDIT_MESH'   

    def execute(self, context):

        import bpy
        import bmesh
        import mathutils

        context = bpy.context
        vl = context.view_layer
        depsgraph = bpy.context.evaluated_depsgraph_get()
        scene = context.scene

        def axis_to_vectors(obj):
            mat = obj.matrix_world
            pos = mat.translation
            zmat = mathutils.Matrix.Translation((0, 0, 1))
            mult = mat @ zmat
            zpos = mult.translation
            delta = zpos - pos
            norm = delta.normalized()
            #print(pos, zpos, delta, norm)
            return (pos, zpos, delta, norm)

        def rotate_object(obj, loc, normal,up_vector= None):
            if up_vector == None:
                up_vector = mathutils.Vector((0, 0, 1))

            angle = normal.angle(up_vector)
            direction = up_vector.cross(normal)

            matrix_rot = mathutils.Matrix.Rotation(angle, 4, direction)
            matrix_translation = mathutils.Matrix.Translation(loc)
            M = matrix_translation @ matrix_rot @ matrix_translation.inverted()

            obj.location = M @ obj.location
            obj.rotation_euler.rotate(M)


        for ob in bpy.context.selected_objects:
            axis_vectors = axis_to_vectors(ob)

            ray_origin = (ob.location[0],ob.location[1],ob.location[2]) # ray origin

            if self.local_z_axis == True:

                ray_direction = axis_vectors[3].to_tuple()
                ray_direction = (ray_direction[0]*(-1),ray_direction[1]*(-1),ray_direction[2]*(-1))
            else:
                ray_direction = (0, 0, -1)


            #hide object before raycast to avoid detecting itself
            ob.hide_set(True)

            hit, loc, norm, idx, obj, mw = scene.ray_cast(depsgraph, ray_origin, ray_direction)
            ob.hide_set(False)
            ob.select_set(True)
            

            if hit:
                ob.location = loc
                
                
                up_vector = axis_vectors[3]
                
                if self.rotate:
                    rotate_object(ob, ob.location, norm, up_vector)               



        return {'FINISHED'}




class lr_select_obj_by_topology(bpy.types.Operator):
    '''Select similiar objects in scene based on vert count, position and edge length'''
    bl_idname = "object.lr_select_obj_by_topology"
    bl_label = "Select objects by topology"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'


    threshold: bpy.props.FloatProperty(
        name='Vert distance threshold',
        description = 'Threshold for selecting identical objects',
        default = 0.01,
        min = 0, soft_max = 1
    ) # type: ignore


    def execute(self, context):


        import bpy
        from mathutils import Vector
        meshwithsamevertcount = []
        vertco = []
        sameobj = []
        vertpos = []
        obj2tarverts_min = []
        obj2tarverts_max = []
        activeobj = bpy.context.object
        for i in bpy.context.view_layer.objects:
            if i.type == 'MESH':
                if len(i.data.vertices) == len(activeobj.data.vertices):

                    if i is not activeobj:
                        meshwithsamevertcount.append(i)
        def compareobjs(obj1, obj2tar, threshold):
            obj1verts = []
            obj2tarverts = []
            for i in range(len(obj2tar.data.vertices)):
                obj2tarverts.append(obj2tar.data.vertices[i].co)
                obj1verts.append(obj1.data.vertices[i].co)




            #add range
            for i in range(len(obj2tarverts)):
        #        for o in range(0,2):
                obj2tarverts_min.append (obj2tarverts[i] - Vector((threshold,threshold,threshold)))
                obj2tarverts_max.append (obj2tarverts[i] + Vector((threshold,threshold,threshold)))

            corr = []

            for i in range(len(obj2tarverts)):
                for o in range (0,3):
                    if obj2tarverts_min[i][o] <= obj1verts[i][o] <=  obj2tarverts_max[i][o]:
                        check = True
                        corr.append(check)
                    else:
                        check = False
                        corr.append(check)
            if False not in corr:
                return(True)
            else:
                return(False)  

        for i in range(len(meshwithsamevertcount)):
        
            if compareobjs(meshwithsamevertcount[i], activeobj, self.threshold) is True:
                meshwithsamevertcount[i].select_set(True)

        return {'FINISHED'}	   
    
           

class lr_deselect_duplicate(bpy.types.Operator):
    '''Deselects all but one instance'''
    bl_idname = "object.lr_deselect_duplicate"
    bl_label = "Deselects multiple repeating geometry"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'



    def execute(self, context):


        import bpy

        #Selected backup
        active_objs = [obj for obj in bpy.context.selected_objects]
        active_objs_data = [obj.data for obj in bpy.context.selected_objects]
        print(active_objs_data)

        active_objs_data_set = set(active_objs_data)
        #Deselect active
        for obj in active_objs:
            obj.select_set(False)
            

        for mesh in active_objs_data_set:
            found = False
            for object in active_objs:
                if found == True:
                    continue
                if object.data == mesh:
                    object.select_set(True)
                    found = True

        return {'FINISHED'}	   
    




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



class OBJECT_OT_SwitchShapeKeyOnMultipleObjects(bpy.types.Operator):
    """Switch to specified shape key index for selected mesh objects"""
    bl_idname = "object.lr_switch_shape_key_on_multiple_objects"
    bl_label = "Switch Shape Key On Multiple Objects"
    bl_options = {'REGISTER', 'UNDO'}
    
    shape_key_index: bpy.props.IntProperty(
        name="Shape Key Index",
        description="Index of the shape key to switch to",
        default=0,
        min=0,
        soft_max=5
    )

    def execute(self, context):
        for obj in context.selected_objects:
            if obj.type != 'MESH':
                continue

            if obj.data.shape_keys and len(obj.data.shape_keys.key_blocks) > self.shape_key_index:
                obj.active_shape_key_index = self.shape_key_index
            else:
                self.report({'WARNING'}, f"Object {obj.name} does not have shape key index {self.shape_key_index}")

        return {'FINISHED'}



class lr_replace_children(bpy.types.Operator):
    """Replaces children on inactive objects from active object.\n Will basically transfer the hierarchy of the active object to the inactive selected objects.\n\nUseful for replacing low poly objects with high poly objects while keeping the same hierarchy."""
    bl_idname = "object.lr_replace_children"
    bl_label = "Replace children"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    #instance_mesh: BoolProperty(name="Children are instances", default=True,)


    def execute(self, context):
        active_obj = bpy.context.object
        active_obj_matrix = active_obj.matrix_world

        selected_objects = bpy.context.selected_objects
        inactive_objs = []
        for j in selected_objects:
            if j is not active_obj:
                inactive_objs.append(j)


        bpy.ops.object.select_grouped(extend=False, type='CHILDREN_RECURSIVE')
        ref_children = [obj for obj in bpy.context.selected_objects]
 



        def instanciate_children_to(object_from,object_to,ref_children_list: list):
            children_list = []
            for ref_children in ref_children_list:
                copy = ref_children.copy()
                children_list.append(copy)
           
            for child,ref_child in zip(children_list, ref_children_list):
                if child.parent is object_from:
                    child.parent = object_to
                    child.matrix_parent_inverse = ref_child.matrix_parent_inverse
                    child.matrix_local = ref_child.matrix_local

                else:
                    parent_list_index = ref_children_list.index(ref_child.parent)
                    child.parent = children_list[parent_list_index]
                    child.matrix_parent_inverse = children_list[parent_list_index].matrix_parent_inverse
                    child.matrix_local = ref_child.matrix_local


                for collection in ref_child.users_collection:
                    collection.objects.link(child)

        def instanciate_children_to_old(object_from,object_to,children_list: list):
            for child,child_new in zip(children,children_new):
                child_matrix_local = child.matrix_local
                child_parent = child.parent

                if child.parent is object_from:
                    child_new.parent = object_to
                    child_new.matrix_local = child_matrix_local
                    #continue
                else:
                    parent_list_index = children_list.index(child_parent)
                    child_new.parent = children_new[parent_list_index]
                    child_new.matrix_local = child_matrix_local

                #Give child a mesh
                for collection in child.users_collection:
                    collection.objects.link(child_new)
                
                if self.instance_mesh == True:
                    child_new.data = child.data
                else:
                    child_new.data = child.data.copy()


        for i in inactive_objs:

            #Remove children on each inactive object children
            bpy.ops.object.select_all(action='DESELECT')
            bpy.context.view_layer.objects.active = i
            bpy.ops.object.select_grouped(extend=False, type='CHILDREN_RECURSIVE')    
            bpy.ops.object.delete(use_global=False, confirm=True)


            #Add instances to each inactive object
            instanciate_children_to(active_obj,i,ref_children)
            


        #Restore selection
        for i in selected_objects:
            i.select_set(True)
        active_obj.select_set(True)
        bpy.context.view_layer.objects.active = active_obj
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


