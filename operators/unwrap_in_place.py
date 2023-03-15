import bpy, bmesh


class LR_Unwrap(bpy.types.Operator):
    bl_idname = "uv.lr_unwrap"
    bl_label = "Unwrap selected in place"
    bl_description = "Unwrap while preserving position and rotation"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'


    def execute(self, context):

        
        selection_set = bpy.ops.uv.select_mode
        uv_select_mode = bpy.context.window.scene.tool_settings.uv_select_mode
        bpy.ops.uv.select_mode(type='VERTEX')
        
        
        if bpy.context.window.scene.tool_settings.use_uv_select_sync == True:
            self.report({'ERROR'}, 'Please  disable sync selection')
            return {'FINISHED'}

        for obj in bpy.context.selected_objects:
            bm = bmesh.from_edit_mesh(obj.data)
            uv = bm.loops.layers.uv.active
            selected_loops = set()
            
           #SelectedLoops
            selected_faces = []
            for face in bm.faces:
                if face.select == True:
                    selected_faces.append(face)
                    for loop in face.loops:
                        if loop[uv].select == True:
                            selected_loops.add(loop)

            


            sel_loops_to_faces = set()
            
            for loop in selected_loops:
                sel_loops_to_faces.add(loop.face)

            sel_loops_to_faces_temp = sel_loops_to_faces.copy()
        
        
            face_islands = []

            for face in selected_faces:
                face.select = False

            while len(sel_loops_to_faces_temp) >= 1:
                for face in sel_loops_to_faces_temp:
                    face.select = True
                    break
                
                bpy.ops.mesh.select_linked(delimit={'SEAM'})

                face_island = [face for face in bm.faces if face.select == True]
                face_island_set = set(face_island)
                face_islands.append(face_island)
                sel_loops_to_faces_temp.difference_update(face_island_set)
                print(sel_loops_to_faces_temp)
                for i in face_island:
                    i.select = False



            for loop in selected_loops:
                loop[uv].select = False


            for island in face_islands:
                for face in island:
                    for loop in face.loops:
                        loop[uv].select = True

            for loop in selected_loops:
                loop[uv].select = False

            
            for face in selected_faces:
                face.select = True

            bpy.ops.uv.unwrap()

            for face in selected_faces:
                for loop in face.loops:
                    loop[uv].select = False


            for loop in selected_loops:
                loop[uv].select = True

            bpy.context.window.scene.tool_settings.uv_select_mode = uv_select_mode
        return {'FINISHED'}

