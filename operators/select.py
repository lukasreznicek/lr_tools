import bpy


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
    


