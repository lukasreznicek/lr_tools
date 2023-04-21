import bpy

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