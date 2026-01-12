import bpy
from bpy.props import BoolProperty

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





