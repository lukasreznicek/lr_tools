#from typing_extensions import IntVar
import bpy, math, bmesh, time, sys, random
from ..utils import lr_functions
from bpy.props import EnumProperty, BoolProperty
from bpy_extras.mesh_utils import mesh_linked_uv_islands
sys.setrecursionlimit(2000)




class LR_Unwrap2(bpy.types.Operator):
    bl_idname = "uv.lr_unwrap2"
    bl_label = "Unwrap selected in place 2"
    bl_description = "Unwrap while preserving position and rotation"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context): 
        return context.mode == 'EDIT_MESH'
    


    method: EnumProperty(
        name="Method",
        items=[
            ("ANGLE_BASED", "Angle Based", ""),
            ("CONFORMAL", "Conformal", ""),
        ]
    )
    fill_holes: BoolProperty(
        name="Fill Holes",
        default=True,
    )

    correct_aspect: BoolProperty(
        name="Correct Aspect",
        default=True,
    )
    


    use_subsurf_data: BoolProperty(
        name="Use Subdivision Surface",
        default=False,
    )



    def execute(self, context):
        start_time = time.time()






        selected_objects = bpy.context.selected_objects
        active_object = bpy.context.view_layer.objects.active

        if bpy.context.scene.tool_settings.use_uv_select_sync == True:
            message = 'Please disable UV Sync mode, cancelled.'
            self.report({'WARNING'}, message)
            return {'FINISHED'}

        for i in selected_objects:
            i.select_set(False)


        # --- Aspect ratio correction ---
        img = lr_functions.get_active_uv_editor_images()
        if img:
            img_resolution = lr_functions.get_image_resolution(img[0])
            
            if img_resolution[0]>img_resolution[1]:
                aspect_correction = [img_resolution[0]/img_resolution[1],1]

            elif img_resolution[0]<img_resolution[1]:
                aspect_correction = [1,img_resolution[1]/img_resolution[0]]
            else:
                aspect_correction = [1,1]

        else:
            aspect_correction = [1,1]





        for ob in selected_objects:

            bpy.ops.object.mode_set(mode = 'OBJECT')
            bpy.context.view_layer.objects.active = ob
            bpy.ops.object.mode_set(mode = 'EDIT')
            


            bm = bmesh.from_edit_mesh(ob.data)
            
            uv_layer = bm.loops.layers.uv.active
        


            selected_faces = [face for face in bm.faces if face.select == True]
            


            # --- If face is deselected also deselect UV loop --->
            deselected_faces = [face for face in bm.faces if face.select == False]
            if deselected_faces:
                lr_functions.deselect_loops_on_faces(bm, deselected_faces, uv_layer)

            selected_loops = lr_functions.get_loop_selection(bm,uv_layer)


            if selected_loops:
                selected_uv_faces = lr_functions.get_selected_uv_faces_from_loops(selected_loops,uv_layer)
                selected_uv_faces_set = set(selected_uv_faces)
                lr_functions.deselect_all_faces(bm)
                

                selected_uv_indexes = [i.index for i in selected_uv_faces]
                selected_uv_indexes_set = set(selected_uv_indexes)



                # --- Select linked polygons ---
                lr_functions.deselect_all_loops(bm, uv_layer)
                
                islands_uv_faces_active = []
                selected_uv_faces_set_temp = selected_uv_faces_set.copy()

                
                #Check for flipped UVs
                flipped_faces = lr_functions.get_flipped_uv_faces(bm, selected_faces)
                selected_uv_faces_set
                flipped_faces_set = set(flipped_faces)

                flipped_uv_faces_in_selection = selected_uv_faces_set.intersection(flipped_faces_set) 
                if len(flipped_uv_faces_in_selection) > 0:
                    has_flipped_faces = True
                    message_flip = 'Some selected UVs are flipped. Results in incorrect unwrap correction.'
                else:
                    has_flipped_faces = False



                #Switch to faces selection mode. Face selection by seam 'bpy.ops.mesh.select_linked(delimit={'SEAM'})'  does not work in all cases in vertex mode.
                if bpy.context.tool_settings.mesh_select_mode[0] == True:

                    vert_mesh_select_mode = True
                    bpy.ops.mesh.select_mode(type="FACE")
                else:
                    vert_mesh_select_mode = False



                while len(selected_uv_faces_set_temp) >= 1:
                    for r in selected_uv_faces_set_temp:
                        random_pick = r
                        break

                    r.select = True
                    
                    bpy.ops.mesh.select_linked(delimit={'SEAM'})

                    face_island = [face for face in bm.faces if face.select == True]


                    island_set = set(face_island)

                    islands_uv_faces_active.append(face_island)
                    selected_uv_faces_set_temp.difference_update(island_set)
                    for i in face_island:
                        i.select = False


                #Return to vertex selection mode if it was active 
                if vert_mesh_select_mode == True:
                    bpy.ops.mesh.select_mode(type="VERT")



                for face in selected_faces:
                    face.select = True

                num_uv_isl = len(islands_uv_faces_active)

                all_faces = set(bm.faces)

                # Get invert selection - inactive islands_index_bm_faces.
                active_faces = set()
                for i in islands_uv_faces_active:
                    active_faces.update(i)
                inactive_faces_set = all_faces.difference(active_faces)



                # --- Hide inactive faces and store original hidden faces ---
                hidden_faces_set = set()
                hidden_faces_to_restore = set()

                for face in inactive_faces_set:
                    if face.hide == True:
                        hidden_faces_set.add(face)
                    else:
                        face.hide = True
                        hidden_faces_to_restore.add(face)


                # --- Islands to islands loops  --- 
                islands_l = []
                for island_face in islands_uv_faces_active:
                    island_l = lr_functions.faces_to_loops(island_face)
                    islands_l.append(island_l)

                # --- Remove loops which were not originally selected, for angle correction ---
                selected_uv_faces_active_islands = []
                for island in islands_uv_faces_active:
                    temp = set(island)
                    temp.intersection_update(selected_uv_faces)
                    selected_uv_faces_active_islands.append(temp)

                islands_l_selected = []
                for i in selected_uv_faces_active_islands:
                    temp = lr_functions.get_list_of_loops_from_faces(i, uv_layer)
                    islands_l_selected.append(temp)
                
                # --- Remove doubles from island_l loops --- 
                islands_verts_selected = []
                for island_verts in islands_l_selected:
                    islands_verts_selected.append(lr_functions.remove_overlapping_loops(island_verts))




                # --- Get islands center for TRANSFORMATION before ---
                center_transform_islands_bef = []
                for island_l_selected in islands_verts_selected:
                    transform_piv_before =  lr_functions.isl_cent(island_l_selected,uv_layer,aspect_correction)          
                    center_transform_islands_bef.append(transform_piv_before)



                # --- Get pivot for ROTATION before ---
                #         Input: [loop1,loop2,loop3]
                #         Output: [piv_x,piv_y]


                def rot_pivot_lst(sel_vert_lst,aspect_correction=[1,1]):

                    x_sum = 0
                    y_sum = 0
                    amount = len(sel_vert_lst)
                    for x in sel_vert_lst:
                        x_sum += (x[uv_layer].uv[0]*aspect_correction[0])
                        y_sum += (x[uv_layer].uv[1]*aspect_correction[1])
                    
                        
                    
                    x_avg = x_sum/amount
                    y_avg = y_sum/amount


                    mid_poi = [x_avg,y_avg]                    
                    
                    return mid_poi



                # def rot_pivot_lst(sel_vert_lst,aspect_correction=[1,1]):
                #     pivotx_b = ((sel_vert_lst[0][uv_layer].uv[0]*aspect_correction[0] + sel_vert_lst[1][uv_layer].uv[0]*aspect_correction[0]) / 2)
                #     pivoty_b = ((sel_vert_lst[0][uv_layer].uv[1]*aspect_correction[1] + sel_vert_lst[1][uv_layer].uv[1]*aspect_correction[1]) / 2)
                #     # mid_poi_before = [pivotx_b,pivoty_b]


                #     mid_poi = [pivotx_b,pivoty_b]                    
                    
                #     return mid_poi



                rot_piv_islds_bef = []
                for i in islands_verts_selected:
                    rot_piv_islds_bef.append(rot_pivot_lst(i,aspect_correction))


                # --- Loop lenght in islands before, SCALE ---
                loop_length_islds_bef = []
                for i in islands_verts_selected:
                    loop_length_islds_bef.append(lr_functions.uv_loops_length(i,uv_layer,aspect_correction))


                angle_up_vert_bef = []
                for j,i in enumerate(islands_verts_selected):
                    temp = lr_functions.cal_angle(rot_piv_islds_bef[j],i,uv_layer,aspect_correction)
                    angle_up_vert_bef.append(temp)

                for kk in 


                # ---------------------------------------------------------------------------- #
                #                                    Unwrap                                    #
                # ---------------------------------------------------------------------------- #

                bpy.ops.uv.unwrap(method=self.method,
                                fill_holes=self.fill_holes,
                                correct_aspect=self.correct_aspect,
                                use_subsurf_data=self.use_subsurf_data,
                                margin=0)

                # ---------------------------------------------------------------------------- #


                # --- Get pivot for ROTATION after ---
                rot_piv_islds_aft = []
                for i in islands_verts_selected:
                    rot_piv_islds_aft.append(rot_pivot_lst(i,aspect_correction))


                # --- Loop lenght in islands after, SCALE---
                loop_length_islds_aft = []
                for i in islands_verts_selected:
                    temp = lr_functions.uv_loops_length(i,uv_layer,aspect_correction)
                    loop_length_islds_aft.append(temp)



                # --- Function: get angle between local up axis and uv point after ---
                angle_up_vert_aft = []
                for j,i in enumerate(islands_verts_selected):
                    temp = lr_functions.cal_angle(rot_piv_islds_aft[j],i,uv_layer,aspect_correction)
                    angle_up_vert_aft.append(temp)


                # --- Calculate correction values ---
                def cor_val(ang_before,ang_after):
                    cor_angle = []
                    for i,j in zip(ang_before, ang_after):
                        if i or j != False:    


                            cor_v = (j - i)
                            cor_angle.append(cor_v)
                        else:
                            cor_angle.append(False)
                
                    hj = 0
                    hi = 0
                    for tg in cor_angle:
                        if tg != False:
                            while tg < 0:
                                tg += 360                        
                            while tg > 360:
                                tg -= 360

                            hi += math.sin(math.radians(tg))
                            hj += math.cos(math.radians(tg))
                        else:
                            continue

                    calc_a = math.atan2(hi, hj)
                    cor_fin = math.degrees(calc_a)
                    return cor_fin



                isl_fin_cor_values = []
                for i,j in zip(angle_up_vert_bef,angle_up_vert_aft):
                    temp = cor_val(i,j)
                    isl_fin_cor_values.append(temp)
                

                for n in range(0,num_uv_isl):

                    # --- Deselect all loops ---
                    lr_functions.deselect_all_loops(bm, uv_layer)


                    # --- Select island_l ---
                    lr_functions.select_loops_on_faces(bm, islands_uv_faces_active[n], uv_layer)

                    # --- Fix rotation ---
                    bpy.ops.transform.rotate(value= math.radians(isl_fin_cor_values[n]), orient_axis='Z', orient_type='VIEW', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='VIEW', mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)

                    
                    # --- Scale correction ---
                    scale_sep = []
            
                    for i,j in zip(loop_length_islds_bef[n],loop_length_islds_aft[n]):
                        if j == 0:
                            print('DIVISION BY ZERO, FIX')
                            j = 0.0001
                        scale_sep.append(i/j)
                        
                    scale_diff = (sum(scale_sep))/(len(scale_sep))

                    bpy.ops.transform.resize(value=(scale_diff, scale_diff, scale_diff), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL')

                    
                    # --- Transform correction ---
                    
                    # --- Get islands center for TRANSFORMATION after ---
                    transform_piv_after =  lr_functions.isl_cent(islands_verts_selected[n],uv_layer,aspect_correction)          
                    
                    transf_cor_x = center_transform_islands_bef[n][0]-transform_piv_after[0]
                    transf_cor_y = center_transform_islands_bef[n][1]-transform_piv_after[1]
                    bpy.ops.transform.translate(value=(transf_cor_x, transf_cor_y, 0), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
        



                for face in hidden_faces_to_restore:
                    face.hide = False


                lr_functions.deselect_all_loops(bm, uv_layer)
                for i in selected_loops:
                    i[uv_layer].select = True
                
                bmesh.update_edit_mesh(ob.data)

                if has_flipped_faces == True:
                    self.report({'WARNING'}, message_flip)

        #------------------------------------------------------------------------------------------------------------------------------------------------------------------------#



        bpy.ops.object.mode_set(mode = 'OBJECT')
        for o in selected_objects:
            o.select_set(True)
        bpy.context.view_layer.objects.active = active_object
        bpy.ops.object.mode_set(mode = 'EDIT')





        stop_time = time.time() - start_time
        #message = 'Rotation: '+format(cor_fin, '.2f')+'°'+', Scale: '+format(scale_diff, '.2f')+ ', Moved UV: '+format(transf_cor_x, '.2f')+', '+format(transf_cor_y, '.2f', )+ ', Time: '+ format(stop_time, '.2f')+'s'
        message = ' Time: '+ format(stop_time, '.2f')+'s'
        self.report({'INFO'}, message)
        
        
        return {'FINISHED'}