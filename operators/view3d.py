import bpy, bmesh, os, re, time
from mathutils import Vector, Matrix
from ..utils import lr_functions
from collections import defaultdict
from collections import OrderedDict
from .. import config



def snap_cursor_to_active_with_rotation(context):
    obj = context.active_object
    if obj is None:
        return False

    scene = context.scene
    cursor = scene.cursor

    # Set cursor location to active object's world location
    cursor.location = obj.matrix_world.translation

    # Transfer rotation from object's world matrix to cursor
    # Preserve rotation mode (QUATERNION or Euler)

    if obj.rotation_mode == 'QUATERNION':
        cursor.rotation_mode = 'QUATERNION'
        cursor.rotation_quaternion = obj.matrix_world.to_quaternion()
    else:
        # Use the object's rotation_mode as the Euler order
        cursor.rotation_mode = obj.rotation_mode
        cursor.rotation_euler = obj.matrix_world.to_euler(obj.rotation_mode)
    return True  


class VIEW3D_OT_snap_cursor_to_active(bpy.types.Operator):
    """Snap 3D cursor to active object and copy its world rotation"""
    bl_idname = "view3d.lr_snap_cursor_to_active"
    bl_label = "Snap Cursor to Active (with Rotation)"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        ok = snap_cursor_to_active_with_rotation(context)
        if not ok:
            self.report({'WARNING'}, "No active object to snap to")
            return {'CANCELLED'}
        return {'FINISHED'}




# class VIEW3D_OT_cursor_grab(bpy.types.Operator):
#     """Grab with temporary cursor pivot/orientation"""
#     bl_idname = "view3d.cursor_grab"
#     bl_label = "Cursor Grab (Temporary Settings)"
#     bl_options = {'REGISTER', 'UNDO'}

#     # store old settings
#     # old_pivot: bpy.props.EnumProperty(items=bpy.types.ToolSettings.bl_rna.properties['transform_pivot_point'].enum_items)
#     # old_orient: bpy.props.EnumProperty(items=bpy.types.ToolSettings.bl_rna.properties['transform_orientation_slots'].enum_items)
# # bpy.context.scene.transform_orientation_slots[0].type = 'CURSOR'
#     initial_orient = None
#     initial_pivot = None


#     def invoke(self, context, event):
#         # ts = context.tool_settings

#         # Save current settings
#         self.initial_orient = bpy.context.scene.transform_orientation_slots[0].type
#         self.initial_pivot  = bpy.context.scene.tool_settings.transform_pivot_point
#         # self.old_pivot = ts.transform_pivot_point
#         # self.old_orient = ts.transform_orientation_slots[0].type

#         # Apply temporary settings
#         bpy.context.scene.tool_settings.transform_pivot_point = 'CURSOR'
#         bpy.context.scene.transform_orientation_slots[0].type = 'CURSOR'

#         # Call modal Grab
#         bpy.ops.transform.translate('INVOKE_DEFAULT')

#         # Add a modal handler to detect when Grab finishes
#         context.window_manager.modal_handler_add(self)
#         return {'RUNNING_MODAL'}

#     def modal(self, context, event):
#         # When Grab finishes, Blender sends a FINISHED or CANCELLED event
#         if event.type in {'LEFTMOUSE', 'RIGHTMOUSE', 'ESC'}:
#             # Restore original settings

#             bpy.context.scene.tool_settings.transform_pivot_point= self.initial_pivot
#             bpy.context.scene.transform_orientation_slots[0].type = self.initial_orient

#             return {'FINISHED'}

#         return {'RUNNING_MODAL'}


def get_nereast_parallel_axis_from_local_obj_rotation():
    import mathutils
    # Get the active area and its space data
    area = bpy.context.area
    space = area.spaces.active
    region_3d = space.region_3d

    # Get the camera view rotation quaternion
    camera_quat = region_3d.view_rotation

    # Get the selected object
    obj = bpy.context.object

    # Ensure the object has been selected and is valid
    if obj is None or obj.type != 'MESH':
        print("Please select a valid mesh object.")
    else:
        # Get the object's world transformation matrix
        obj_matrix = obj.matrix_world

        # Extract the object's local axes as vectors
        x_axis_local = mathutils.Vector((1, 0, 0))
        y_axis_local = mathutils.Vector((0, 1, 0))
        z_axis_local = mathutils.Vector((0, 0, 1))

        # Convert local axes to world space vectors
        x_axis_world = obj_matrix @ x_axis_local
        y_axis_world = obj_matrix @ y_axis_local
        z_axis_world = obj_matrix @ z_axis_local

        # Convert camera quaternion to a view direction vector (assuming no scaling)
        camera_view_direction = camera_quat @ mathutils.Vector((0, 0, -1))

        # print(f'Camera Dir vector: {camera_view_direction}')
        # Compute the dot products between the camera view direction and object local axes
        dot_x = camera_view_direction.dot(x_axis_world.normalized())
        dot_y = camera_view_direction.dot(y_axis_world.normalized())
        dot_z = camera_view_direction.dot(z_axis_world.normalized())

        # Determine the axis with the highest dot product
        dot_products = {'X': dot_x, 'Y': dot_y, 'Z': dot_z}
        dot_products_abs = {'X': abs(dot_x), 'Y': abs(dot_y), 'Z': abs(dot_z)}

        most_parallel_axis = max(dot_products_abs, key=dot_products_abs.get)

        print(f'Axis: {most_parallel_axis}, Is positive:  {False if dot_products[most_parallel_axis] < 0 else True}')
        # Returns most parellel axis and if positive or negative direction
        return (most_parallel_axis, False if dot_products[most_parallel_axis] < 0 else True)

        # # Print the results
        # print(f"Most parallel axis to the camera view direction: {most_parallel_axis}")
        # print(f"Dot Products - X: {dot_x}, Y: {dot_y}, Z: {dot_z}")


class LR_OT_view_object_rotate(bpy.types.Operator):
    bl_idname = "lr.view_object_rotate"
    bl_label = "Rotates object or UVs 90° based on viewport position"
    bl_options = {'REGISTER', 'UNDO'}
    
    # view_rotate_left: bpy.props.BoolProperty(name="Rotate Left", default= False,options={'SKIP_SAVE'})    
    rotate_left: bpy.props.BoolProperty(name="Rotate Left", default= False, options={'SKIP_SAVE'})  

    @classmethod
    def poll(cls, context):
        # Check if the active space is the UV/Image Editor
        return context.space_data.type in {'IMAGE_EDITOR', 'VIEW_3D'}
    
    def execute(self, context):        
        #Object Rotation    

        if bpy.context.space_data.type == "VIEW_3D":
           
           if bpy.context.scene.transform_orientation_slots[0].type == "LOCAL":
                val = get_nereast_parallel_axis_from_local_obj_rotation()
                # if val[0] == 'X' and val[1] == True:
                if self.rotate_left == False:
                    
                    bpy.ops.transform.rotate(value=-1.5708 if val[1] == True else 1.5708, orient_type='LOCAL', orient_axis=val[0])
                else:
                    bpy.ops.transform.rotate(value=1.5708 if val[1] == True else -1.5708, orient_type='LOCAL', orient_axis=val[0])

           else:
                axis = lr_functions.get_view_orientation()
                if self.rotate_left == False:
                    #FRONT, LEFT, BOTTOM
                    if axis[1] == True:
                        bpy.ops.transform.rotate(value=1.5708, constraint_axis=(axis[0][0], axis[0][1], axis[0][2]))
                    #BACK, RIGHT, TOP
                    if axis[1] == False:
                        bpy.ops.transform.rotate(value=-1.5708, constraint_axis=(axis[0][0], axis[0][1], axis[0][2]))


                #Rotate to left
                if self.rotate_left == True:
                    #FRONT, LEFT, BOTTOM
                    if axis[1] == True:
                        bpy.ops.transform.rotate(value=-1.5708, constraint_axis=(axis[0][0], axis[0][1], axis[0][2]))
                    #BACK, RIGHT, TOP
                    if axis[1] == False:
                        bpy.ops.transform.rotate(value=1.5708, constraint_axis=(axis[0][0], axis[0][1], axis[0][2]))

        #UV Rotation
        if bpy.context.space_data.type == "IMAGE_EDITOR":
            if self.rotate_left:
                bpy.ops.transform.rotate(value=-1.5708, orient_axis='Z', orient_type='VIEW', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='VIEW')
            else:
                bpy.ops.transform.rotate(value=1.5708, orient_axis='Z', orient_type='VIEW', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='VIEW')
            return {'FINISHED'}


        return {'FINISHED'}




