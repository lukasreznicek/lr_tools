import bpy
from bpy.props import BoolProperty

class lr_replace_children(bpy.types.Operator):
    """Replaces children on inactive objects from active object"""
    bl_idname = "object.lr_replace_children"
    bl_label = "Replace children"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    instance_mesh: BoolProperty(name="Children are instances", default=True,)


    def execute(self, context):
        active_obj = bpy.context.object
        active_obj_matrix = active_obj.matrix_world

        selected_objects = bpy.context.selected_objects
        inactive_objs = []
        for j in selected_objects:
            if j is not active_obj:
                inactive_objs.append(j)


        bpy.ops.object.select_grouped(extend=False, type='CHILDREN_RECURSIVE')

        children = [obj for obj in bpy.context.selected_objects]


        #Cheaper version to check whether mesh exist in scene. If not, create temporary mesh.
        try:
            bpy.data.meshes['LR_TempDelete_ReplaceChildrenScript']
        except:
            bpy.data.meshes.new('LR_TempDelete_ReplaceChildrenScript')
        

        def instanciate_children_to(object_from,object_to,children_list: list):
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
            children_new = []
            for child in children:
                #New object and temporary mesh
                #Update with correct existing mesh
                new_child = bpy.data.objects.new(child.name,bpy.data.meshes['LR_TempDelete_ReplaceChildrenScript'])
                children_new.append(new_child)



            #Remove children on each inactive object children
            bpy.ops.object.select_all(action='DESELECT')
            bpy.context.view_layer.objects.active = i
            bpy.ops.object.select_grouped(extend=False, type='CHILDREN_RECURSIVE')    
            bpy.ops.object.delete(use_global=False, confirm=True)


            #Add instances to each inactive object
            instanciate_children_to(active_obj,i,children)
            



        #Remove temporary mesh
        bpy.data.meshes.remove(bpy.data.meshes['LR_TempDelete_ReplaceChildrenScript'])

        #Restore selection

        for i in selected_objects:
            i.select_set(True)
        active_obj.select_set(True)
        bpy.context.view_layer.objects.active = active_obj
        return {'FINISHED'}





