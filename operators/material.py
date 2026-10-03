import bpy, bmesh, os, re, time
from mathutils import Vector, Matrix
from ..utils import lr_functions
from collections import defaultdict
from collections import OrderedDict
from .. import config


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



class OBJECT_OT_lr_assign_checker(bpy.types.Operator):
    bl_idname = "object.lr_assign_checker"
    bl_label = "Assigns checker texture"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):     
        # script_folder = bpy.utils.script_paths()
        # script_folder.reverse()
        # texture_path = None

        # # print(os.path.dirname(os.path.realpath(__file__)))

        # #Find script folder with addon
        # found = False
        # for path in script_folder:
        #     path = os.path.join(path,'addons')
        #     if os.path.exists(path):
        #         if 'lr_tools' in os.listdir(path) or 'lr_tools-master' in os.listdir(path):
        #             texture_full_path = os.path.join(path,'lr_tools','textures',texture_name)
        #             found = True

        # if found == False:
        #     message = 'Addon folder name in scripts directory should be: lr_tools. Please Rename.'
        #     self.report({'ERROR'}, message)
        #     return {'FINISHED'}

        texture_name = 'T_CheckerMap_A.png'
        texture_full_path = os.path.join(config.addon_folder_location,'textures',texture_name)
        #Load image
        bpy.data.images.load(texture_full_path, check_existing=True)
        
    
        #Create material function
        if 'MF_LR_Checker' not in bpy.data.node_groups:
            mf_lr_checker = bpy.data.node_groups.new('MF_LR_Checker','ShaderNodeTree')

            mf_lr_checker_input_socket = bpy.data.node_groups['MF_LR_Checker'].interface.items_tree.data.new_socket('ShaderInput',in_out='INPUT', socket_type= 'NodeSocketShader')
            mf_lr_checker_output_socket = bpy.data.node_groups['MF_LR_Checker'].interface.items_tree.data.new_socket('ShaderOutput',in_out='OUTPUT', socket_type= 'NodeSocketShader')


            tex_sample = bpy.data.node_groups['MF_LR_Checker'].nodes.new('ShaderNodeTexImage')  #Create texture node
            group_output = bpy.data.node_groups['MF_LR_Checker'].nodes.new('NodeGroupOutput')   #Create function output
            group_input = bpy.data.node_groups['MF_LR_Checker'].nodes.new('NodeGroupInput')     #Create function input
            #nodes = bpy.data.node_groups['LR_Checker'].nodes

            bpy.data.node_groups['MF_LR_Checker'].links.new(group_output.inputs[0],tex_sample.outputs[0])   #Link 
            tex_sample.image = bpy.data.images[texture_name]

        # #Exec

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

                        # print (f'{node_output_input_source = }')
                        node_output_input_node = node.inputs['Surface'].links[0].from_node
                        # print (f'{node_output_input_node = }')
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

#Slow Disabled

