import bpy, math, bmesh, time, sys
from ..utils import lr_functions
from bpy.props import EnumProperty, BoolProperty
from bpy_extras.mesh_utils import mesh_linked_uv_islands
sys.setrecursionlimit(2000)


class LR_Unwrap(bpy.types.Operator):
    bl_idname = "uv.lr_unwrap_vertex"
    bl_label = "Vertex unwrap"
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
        default=False,
    )
    use_subsurf_data: BoolProperty(
        name="Use Subdivision Surface",
        default=False,
    )



    def execute(self, context):

        start_time = time.time()

        ob = bpy.context.object
        bm = bmesh.from_edit_mesh(ob.data)
        uv_layer = bm.loops.layers.uv.active

        sel_loops_islands = []
        bm.faces.ensure_lookup_table()

        selected_loops_backup = lr_functions.get_loop_selection(bm,uv_layer)
        
        faces_by_islands =  lr_functions.get_faces_by_seam_islands(bm,ob.data)


        #elected_polys = [f for f in bm.faces if f.select == True]

            
        num_uv_isl_all = len(faces_by_islands)


        stop_time = time.time() - start_time
        #message = 'Rotation: '+format(cor_fin, '.2f')+'°'+', Scale: '+format(scale_diff, '.2f')+ ', Moved UV: '+format(transf_cor_x, '.2f')+', '+format(transf_cor_y, '.2f', )+ ', Time: '+ format(stop_time, '.2f')+'s'
        message = ' Time: '+ format(stop_time, '.2f')+'s'
        self.report({'INFO'}, message)
        
        
        return {'FINISHED'}
