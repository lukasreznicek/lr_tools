import bpy,re

class lr_export_but_one_material(bpy.types.Operator):

    """ Exports objects prepared for Substance Painter mask creation. Exported mesh will have only one material.
        Exception mat: 'Occluder'
        Requires Blender for Unreal Engine addon.
    """

    bl_idname = "object.lr_export_but_one_material"
    bl_label = "Exports with one material"
    
    def execute(self, context):

        act_obj = bpy.context.active_object
        ina_objmain = []



        new_help = act_obj.copy()
        bpy.context.scene.collection.objects.link(new_help)

        # for i in sel_obj:
        #     if i == bpy.context.active_object:
        #         pass
        #     else:
        #         ina_objmain.append(i)
        bpy.ops.object.select_grouped(type='CHILDREN_RECURSIVE')

        ina_objmain = [i for i in bpy.data.objects if i.select_get() == True]



        def FilterAndDuplicateSelMeshes(objs):
            #import fnmatch
            scn = bpy.context.scene   
            dupl_meshs = []

            for i in objs:
            
                if i.type == 'MESH':
                    new_obj = i.copy()
                    new_obj.data = i.data.copy()
                    scn.collection.objects.link(new_obj)
                    dupl_meshs.append(new_obj)

            return dupl_meshs       



        children_duplicated = FilterAndDuplicateSelMeshes(ina_objmain)

        #REMOVES ACTIVE OBJECT FROM SELECTION AND CHANGES ACTIVE OBJECT, FOR LATER OPERATORS
        act_obj.select_set(False)
        context.view_layer.objects.active = children_duplicated[-1]

        # def removesalluvmapsbut(objects,keepuvmapname = None):
        #     uv_layers = []

        #     for i in objects:
        #         k = 0
        #         if keepuvmapname in i.data.uv_layers: 
        #             while len(i.data.uv_layers)-1 > 0:
        #                 if i.data.uv_layers[0+k].name == keepuvmapname:
        #                     k+=1
        #                     continue
        #                 else:
        #                     i.data.uv_layers.remove(i.data.uv_layers[0+k])

        #         else:
        #             while len(i.data.uv_layers)-1 > 0:
                    
        #                     i.data.uv_layers.remove(i.data.uv_layers[1])




        # removesalluvmapsbut(children_duplicated,keepuvmapname = 'MaskUV')  


        for i in children_duplicated:

            bpy.context.view_layer.objects.active = i
            len(i.material_slots)
            while len(i.material_slots) > 1:
                i.active_material_index = len(i.material_slots)-1
                bpy.ops.object.material_slot_remove()


        #SET MATERIAL
        mat = bpy.data.materials.new(name="MaskBake")
        
        for i in children_duplicated:
            link = i.material_slots[0].link

            #If material is linked to data:
            if link == 'DATA':
                if i.data.materials[0].name != 'Occluder':
                    i.data.materials[0] = bpy.data.materials['MaskBake']

            #If material is linked to object:
            if link == 'OBJECT':
                if i.material_slots[0].name != 'Occluder':
                    i.material_slots[0].material = bpy.data.materials['MaskBake']



            # if i.data.materials[0].name != 'Occluder':
            #     i.data.materials[0] = bpy.data.materials['MaskBake']
            #     if i.material_slots:
            #         i.material_slots[0].material = bpy.data.materials['MaskBake']

        #PARENT TO
        for i in children_duplicated:
            matrix = i.matrix_world
            i.parent = new_help
            i.matrix_world = matrix


        ##SELECTS ACTIVE OBJECT
        bpy.ops.object.select_all(action='DESELECT')
        
        new_help.select_set(True)
        context.view_layer.objects.active = new_help

        #Naming
        store_name = act_obj.name
        new_help.name = store_name


        #EXPORT
        bpy.ops.object.exportforunreal()



        #REMOVE OBJS
        bpy.ops.object.select_all(action='DESELECT')

        for i in children_duplicated:
            i.select_set(True)
            
        new_help.select_set(True)

        bpy.ops.object.delete() 

        act_obj.name = store_name
        return {'FINISHED'}




class lr_exportformask(bpy.types.Operator):

    """ Exports objects with one UV Set and one material.
        Steps:
            Blender for UE addon.
            All meshes must have UVSet named 'MaskUV'.
            Select objects to export and one active helper used as a pivot"""

    bl_idname = "object.lr_exportformask"
    bl_label = "LR Mask export - Export objects for mask"
    def execute(self, context):

        sel_obj = bpy.context.selected_objects
        act_obj = bpy.context.active_object
        ina_objmain = []


        if len(act_obj.children) != 0:
            message = 'Not exported. Please select parent without children.'
            self.report({'INFO'}, message)
            return {'FINISHED'}


        for i in sel_obj:
            if i == bpy.context.active_object:
                pass
            else:
                ina_objmain.append(i)


        def FilterAndDuplicateSelMeshes(objs):
            import fnmatch
            scn = bpy.context.scene   
            dupl_meshs = []

            store_names = []
            for i in objs:
                if i.type == 'MESH':
                    store_names.append(i.name)
                    new_obj = i.copy()

                    new_obj.name = i.name

                    #ASSIGN DUPLICATED OBJECT INTO THE SAME COLLECTION AS ORIGINAL OBJ (For material assignment)
                    for collect in i.users_collection:
                        collect.objects.link(new_obj)

                    new_obj.data = i.data.copy()
                    #No need to link to scene. 
                    #scn.collection.objects.link(new_obj)
                    dupl_meshs.append(new_obj)

            return dupl_meshs, store_names      



        ina_obj,stored_names = FilterAndDuplicateSelMeshes(ina_objmain)

        #REMOVES ACTIVE OBJECT FROM SELECTION AND CHANGES ACTIVE OBJECT, FOR LATER OPERATORS
        act_obj.select_set(False)
        context.view_layer.objects.active = ina_obj[-1]

        def removesalluvmapsbut(objects,keepuvmapname = None):
            uv_layers = []

            for i in objects:
                k = 0
                if keepuvmapname in i.data.uv_layers: 
                    while len(i.data.uv_layers)-1 > 0:
                        if i.data.uv_layers[0+k].name == keepuvmapname:
                            k+=1
                            continue
                        else:
                            i.data.uv_layers.remove(i.data.uv_layers[0+k])

                else:
                    while len(i.data.uv_layers)-1 > 0:
                    
                            i.data.uv_layers.remove(i.data.uv_layers[1])




        removesalluvmapsbut(ina_obj,keepuvmapname = 'MaskUV')  


        for i in ina_obj:
            bpy.context.view_layer.objects.active = i

            while len(i.material_slots) > 1:
                i.active_material_index = len(i.material_slots)-1
                bpy.ops.object.material_slot_remove()


        #CREATE MATERIAL
        all_mats = []
        all_collections = []
        collection_name_for_occluder = 'occluder'
        mat_occluder_name = 'MaskOccluder'
        mask_id_collection_tag = '_id'
        mask_base_name = 'M_BakeMat'




        for material in bpy.data.materials:
            all_mats.append(material.name)

        # for collection in bpy.data.collections:
        #     all_collections.append(collection.name)
        
        # if 'MaskBake_ID1' not in all_mats:
        #     mat = bpy.data.materials.new(name='MaskBake_ID1')



        # if collection_name_for_occluder in all_collections:
        #     if mat_occluder_name not in all_mats:
        #         mat_occluder = bpy.data.materials.new(name=mat_occluder_name)
        

        #SET MATERIAL
        for obj in ina_obj: 
            
            # link = i.material_slots[0].link

            # #If material is linked to data:
            # if link == 'DATA':
            #     if i.data.materials[0].name != mat_occluder_name:
            #         i.data.materials[0] = bpy.data.materials['MaskBake']

            # #If material is linked to object:
            # if link == 'OBJECT':
            #     if i.material_slots[0].name != mat_occluder_name:
            #         i.material_slots[0].material = bpy.data.materials['MaskBake']


            # #If object is in collection containing 'Occluder' assign material occluder.
            # for collection in i.users_collection:
            #     collection_name = collection.name
            #     collection_name = collection_name.lower()
            #     if collection_name_for_occluder in collection_name:
            #         i.material_slots[0].material = bpy.data.materials[mat_occluder_name]

            #If object is in collection containing '_ID' assign material.
            link = obj.material_slots[0].link 

            for collection in obj.users_collection:
                collection_name = collection.name
                collection_name_lower = collection_name.lower()
                match = re.search('(?i)_id(\d+)', collection_name)


                if 'occluder' in collection_name_lower:
                    if mat_occluder_name not in all_mats:
                        mat_occluder = bpy.data.materials.new(name=mat_occluder_name)
                    if link == 'OBJECT':
                        obj.material_slots[0].material = bpy.data.materials[str(mat_occluder_name)]

                    if link == 'DATA':
                        obj.data.materials[0] = bpy.data.materials[mat_occluder_name]   

    
                if match:
                    #Create material if it isn't in scene.
                    mat_name = mask_base_name+'_ID'+match.group(1)

                    if mat_name not in all_mats:
                        bpy.data.materials.new(name=mat_name)
                    
                    if link == 'OBJECT':

                        obj.material_slots[0].material = bpy.data.materials[str(mat_name)]

                    if link == 'DATA':

                        obj.data.materials[0] = bpy.data.materials[str(mat_name)]




        #PARENT TO
        for i in ina_obj:
            matrix = i.matrix_world
            i.parent = act_obj
            i.matrix_world = matrix


        ##SELECTS ACTIVE OBJECT
        bpy.ops.object.select_all(action='DESELECT')
        
        act_obj.select_set(True)
        context.view_layer.objects.active = act_obj

        #EXPORT
        bpy.ops.object.exportforunreal()



        #REMOVE OBJS
        bpy.ops.object.select_all(action='DESELECT')


        for i in ina_obj:
            #i.select_set(True)

            bpy.data.meshes.remove(i.data, do_unlink=True)

        #bpy.ops.object.delete() 
        
        #Restore names
        for name,obj in zip(stored_names,ina_objmain):
            obj.name = name


        return {'FINISHED'}










# class lr_meshcleanup(bpy.types.Operator):
#     bl_idname = "object.lr_meshcleanup"
#     bl_label = "LR Mask export -  01 Mesh cleanup for export"
#     def execute(self, context):
#         selection = bpy.context.selected_objects


#         #print(len(sel_obj))
#         sel_obj = bpy.context.selected_objects
#         act_obj = bpy.context.active_object
#         ina_obj = []

#         for i in sel_obj:
#             if i == bpy.context.active_object:
#                 pass
#             else:
#                 ina_obj.append(i)


#         def FilterAndDuplicateSelMeshes(objs):
#             import fnmatch
#             scn = bpy.context.scene   
#             dupl_meshs = []

#             for i in objs:
            
#                 if i.type == 'MESH':
#                     new_obj = i.copy()
#                     new_obj.data = i.data.copy()
#                     scn.collection.objects.link(new_obj)
#                     dupl_meshs.append(new_obj)

#             return dupl_meshs             

#         def FilterAndDuplicateGroupProObj(objs):
#             import fnmatch
#             scn = bpy.context.scene
#             dupl_gPro = []
#             for i in objs:
#                 if i.type == 'EMPTY' and fnmatch.fnmatch(i.name, 'gp_*'):
#                     new_obj = i.copy()
#                     scn.collection.objects.link(new_obj)
#                     dupl_gPro.append(new_obj)

#             return dupl_gPro

#         def gprocleanup(gproobjs):
#             gprocleanupmeshes = []
#             bpy.ops.object.select_all(action='DESELECT')
#             for i in gproobjs:
#                 i.select_set(True)
#             bpy.context.view_layer.objects.active = gproobjs[0]
#             bpy.ops.object.gpro_converttogeo(maxDept=10)
#             bpy.ops.object.make_single_user(object=True, obdata=True, material=True, animation=False)
#             for n in bpy.context.selected_objects:
#                 gprocleanupmeshes.append(n)

#             return gprocleanupmeshes


#         dupl_meshes = FilterAndDuplicateSelMeshes(sel_obj)      
#         dupl_gpro = FilterAndDuplicateGroupProObj(sel_obj)

#         new_objs = []
#         if dupl_gpro:
#             gp_cleanedmeshes = gprocleanup(dupl_gpro)
#             new_objs.extend(gp_cleanedmeshes)


#         new_objs.extend(dupl_meshes)
        

#         print(new_objs)



                
#         bpy.ops.object.select_all(action='DESELECT')
#         for i in new_objs:
#             i.select_set(True)

#         #APPLY SCALE
#         bpy.ops.object.transform_apply(location = False, scale = True, rotation = True)
#         #SET ACTIVE OBJ
#         bpy.context.view_layer.objects.active = new_objs[0]
#         #COLLAPSE ALL MATERIALS
#         bpy.ops.object.convert(target='MESH')



#         ##SET TO EDITMODE
#         #bpy.ops.object.mode_set(mode='EDIT')
#         ##SELECT ALL POLYGONS
#         #bpy.ops.mesh.select_all(action='SELECT')
#         #bpy.ops.uv.select_all(action='SELECT')
#         #bpy.ops.uv.average_islands_scale()
#         #bpy.ops.object.mode_set(mode='OBJECT')


#         return {'FINISHED'}	   
    
    




# class lr_prepareuvsformask(bpy.types.Operator):
#     bl_idname = "object.lr_prepareuvsformask"
#     bl_label = "LR Mask export - 02 Prepares UVs"
#     def execute(self, context):

#         sel_obj = bpy.context.selected_objects
#         act_obj = bpy.context.active_object
#         ina_obj = []
#         uvname = 'MaskUV'


#         for i in sel_obj:
#             if i == bpy.context.active_object:
#                 pass
#             else:
#                 ina_obj.append(i)


#         for i in sel_obj:
#             if uvname in i.data.uv_layers:
#                 continue
#             else:
#                 i.data.uv_layers[0].active = True
#                 i.data.uv_layers.new(name = uvname)

        
        
#         positionche = []

#         for i in sel_obj:
#             i.data.uv_layers[uvname].active = True
#             positionche.append(i.data.uv_layers.active_index)


#         for i in positionche:
#             if i != positionche[0]:
#                 self.report({'WARNING'}, 'Fix positions of '+uvname+' UV channel before continuing.')




#         bpy.ops.object.mode_set(mode='EDIT')
#         bpy.ops.mesh.select_all(action='SELECT')
#         #bpy.ops.uv.average_islands_scale()

#         #PACKING

#         bpy.ops.object.preset_set(td_value="2.56")
#         #bpy.ops.object.texel_density_set()
#         bpy.ops.uv.select_all(action='SELECT')
#         bpy.ops.uvpackmaster2.uv_pack()

#         bpy.ops.object.mode_set(mode='OBJECT')


#         return {'FINISHED'}	  





