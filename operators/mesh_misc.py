import bpy, bmesh, os,re
from mathutils import Vector
from ..utils import lr_functions



class MESH_OT_getEdgesLength(bpy.types.Operator):
    bl_idname = "mesh.lr_get_edges_length"
    bl_label = "Outputs length of selected edges"
    bl_options = {'REGISTER', 'UNDO'}

    edges_length: bpy.props.FloatProperty(name="Length: ",unit='LENGTH',precision=5)
    
    def execute(self, context):

        #Execute only if selection is mesh
        if len(bpy.context.selected_objects) != 0:
            if bpy.context.active_object.type == 'MESH':      
                
                
                bm = bmesh.from_edit_mesh(bpy.context.active_object.data)

                def sel_edges_length(bm):
                    length: float = 0
                    for edge in bm.edges:
                        if edge.select == True:
                            length += edge.calc_length()
                    return length

                #Default is meters
                length = sel_edges_length(bm)


                self.edges_length = length

        else:
            self.report({'ERROR'}, "Select object.")
            return {'FINISHED'}


        #self.report({'INFO'}, "Length: " + str(length))
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


class OBJECT_OT_material_slot_remove_unused_on_selected(bpy.types.Operator):
    '''Removes unused material slots on all selected objects. Same as blender default operator but works with multiple object selection'''
    bl_idname = "object.material_slot_remove_unused_on_selected"
    bl_label = "Same as blender default operator but works with multiple object selection."
    bl_options = {'REGISTER', 'UNDO'}

    # @classmethod
    # def poll(cls, context): 
    # 	return context.mode == 'OBJECT'

    def execute(self, context):
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                bpy.ops.object.material_slot_remove_unused()
        return {'FINISHED'}		


class OBJECT_OT_lr_material_cleanup(bpy.types.Operator):
    '''Checks materials for suffixes and assings the lowest material or material without suffix. Intended for removing duplicated materials. Only on selected objects'''
    bl_idname = "object.lr_material_cleanup"
    bl_label = "Checks materials for suffixes and assings the lowest material or material without suffix."
    bl_options = {'REGISTER', 'UNDO'}

    # @classmethod
    # def poll(cls, context): 
    # 	return context.mode == 'OBJECT'

    def execute(self, context):
        src_materials = []
        for src_material in bpy.data.materials:
            src_materials.append(src_material)

        selected_objects = []

        for object in bpy.context.selected_objects:
            if object.type == 'MESH':
                selected_objects.append(object)                            #Will add every instance in case of material assignment to object and not data.
            
        for object in selected_objects:
            for obj_material in object.material_slots:
                if obj_material.name != '':                                     #Empty material slot check
                    res = re.split('(\.\d+$)', obj_material.material.name)
                    if len(res) > 1:
                        matches = []
                        for src_material in src_materials:
                            if re.search(res[0], src_material.name):
                                matches.append(src_material)
                        obj_material.material = matches[0]


        return {'FINISHED'}		






class OBJECT_OT_view_object_rotate(bpy.types.Operator):
    bl_idname = "object.view_object_rotate"
    bl_label = "Rotates object 90° based on viewport position"
    bl_options = {'REGISTER', 'UNDO'}
    
    view_rotate_left: bpy.props.BoolProperty(name="Left", default= False,options={'SKIP_SAVE'})    


    def execute(self, context):
        
        axis = lr_functions.get_view_orientation()

        #Rotate to Right
        if self.view_rotate_left == False:
            #FRONT, LEFT, BOTTOM
            if axis[1] == True:
                bpy.ops.transform.rotate(value=1.5708, constraint_axis=(axis[0][0], axis[0][1], axis[0][2]))
            #BACK, RIGHT, TOP
            if axis[1] == False:
                bpy.ops.transform.rotate(value=-1.5708, constraint_axis=(axis[0][0], axis[0][1], axis[0][2]))


        #Rotate to left
        if self.view_rotate_left == True:
            #FRONT, LEFT, BOTTOM
            if axis[1] == True:
                bpy.ops.transform.rotate(value=-1.5708, constraint_axis=(axis[0][0], axis[0][1], axis[0][2]))
            #BACK, RIGHT, TOP
            if axis[1] == False:
                bpy.ops.transform.rotate(value=1.5708, constraint_axis=(axis[0][0], axis[0][1], axis[0][2]))

            
                    
        return {'FINISHED'}




class OBJECT_OT_lr_assign_checker(bpy.types.Operator):
    bl_idname = "object.lr_assign_checker"
    bl_label = "Assigns checker texture"
    bl_options = {'REGISTER', 'UNDO'}
    
    
    def execute(self, context): 

        script_folder = bpy.utils.script_paths()
        script_folder.reverse()
        texture_path = None

        texture_name = 'T_CheckerMap_A.png'

        #Find script folder with addon
        for path in script_folder:
            path = os.path.join(path,'addons')
            if os.path.exists(path):
                if 'lr_tools' in os.listdir(path):
                    texture_full_path = os.path.join(path,'lr_tools','textures',texture_name)
        else:
            pass
        
        #Load image
        print('Image Path: ', texture_full_path)
        bpy.data.images.load(texture_full_path, check_existing=True)
        
    
        #Create material function
        if 'MF_LR_Checker' not in bpy.data.node_groups:
            mf_lr_checker = bpy.data.node_groups.new('MF_LR_Checker','ShaderNodeTree')
            mf_input = bpy.data.node_groups['MF_LR_Checker'].inputs.new('NodeSocketShader','main_shader_input')
            mf_output = bpy.data.node_groups['MF_LR_Checker'].outputs.new('NodeSocketShader','main_shader_output')
            
            tex_sample = bpy.data.node_groups['MF_LR_Checker'].nodes.new('ShaderNodeTexImage')
            group_output = bpy.data.node_groups['MF_LR_Checker'].nodes.new('NodeGroupOutput')
            group_input = bpy.data.node_groups['MF_LR_Checker'].nodes.new('NodeGroupInput')
            #nodes = bpy.data.node_groups['LR_Checker'].nodes

            bpy.data.node_groups['MF_LR_Checker'].links.new(group_output.inputs[0],tex_sample.outputs[0])
            tex_sample.image = bpy.data.images[texture_name]

        #Exec

        #Go get materials on object         
        obj_materials = []
        for mslot in bpy.context.object.material_slots:
            obj_materials.append(mslot.material)
            

        #LR Material function
        for obj_material in obj_materials:

        

        #Output node
            material_output_check = False
            for node in obj_material.node_tree.nodes:
                #Find/declare output node and it's input
                

                if node.type == "OUTPUT_MATERIAL":
                    material_output_check = True
                    node_output = node
                    
                    if len(node.inputs['Surface'].links) >= 1:
                        node_output_input_source = node.inputs['Surface'].links[0].from_socket
                        node_output_input_node = node.inputs['Surface'].links[0].from_node
                    else:
                        node_output_input_source = False



            #Create/declare output node if does not exist  
            if material_output_check == False:
                node_output = obj_material.node_tree.nodes.new("ShaderNodeOutputMaterial")
                node_output_input_source = False


            #Add MF into shader
            create = True
            if node_output_input_node.type == 'GROUP':
                if node_output_input_node.node_tree.name == 'MF_LR_Checker':
                    create = False
           
            if create == True:
                group = obj_material.node_tree.nodes.new('ShaderNodeGroup')
                group.name = 'LR_Checker' 
                group.node_tree = bpy.data.node_groups['MF_LR_Checker']


                #Relink to new node
                if node_output_input_source != False:
                    obj_material.node_tree.links.new(node_output_input_source, group.inputs[0])   
                obj_material.node_tree.links.new(group.outputs[0], node_output.inputs['Surface'])



        


        
        if texture_full_path == None:
            print('Could not find checker texture')
            return {'FINISHED'}
        else:
            pass

        return {'FINISHED'}


class OBJECT_OT_lr_remove_checker(bpy.types.Operator):
    bl_idname = "object.lr_remove_checker"
    bl_label = "Removes checker texture"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context): 

        obj_materials = []
        for mslot in bpy.context.object.material_slots:
            obj_materials.append(mslot.material)
        
        for obj_material in obj_materials:
            for node in obj_material.node_tree.nodes:
                if node.type == 'GROUP' and node.node_tree.name == 'MF_LR_Checker':
                    if len(node.inputs[0].links) >= 1:
                        obj_material.node_tree.links.new(node.inputs[0].links[0].from_socket,node.outputs[0].links[0].to_socket)
                    
                    obj_material.node_tree.nodes.remove(node)
        



        return {'FINISHED'}

