import bpy



class lr_name_high_poly_bake(bpy.types.Operator):
    """Name inactive object(s) based on active object's name, replacing low poly suffix with high poly suffix, works for substance painter bake name matching . Including suffixes after '_low' \n\nIf Active object is missing _lp suffix, it will be added. \nIf multiple inactive objects(high poly) are selected, they will be numbered"""
    bl_idname = "lr.name_high_poly_bake"
    bl_label = "Copy Active Name to Inactive"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def execute(self, context):

        active_obj = context.active_object
        if active_obj is None or active_obj.type != 'MESH':
            self.report({'WARNING'}, "Active object must be a mesh.")
            return {'CANCELLED'}
        
        
        selected = context.selected_objects
        inactive_objs = [obj for obj in selected if obj != active_obj and obj.type == 'MESH']
        if not active_obj or len(selected) < 2:
            self.report({'WARNING'}, "Select inactive object(s) (high poly) and active obj (low poly).")
            return {'CANCELLED'}

        active_name = active_obj.name
        has_suffix = False
        multiple_inactive = False
        new_name = active_name

        if(len(inactive_objs)>1):
            multiple_inactive = True
        
        naming_values = {"_lp": "_hp", 
                         "_low": "_high", 
                         "_Lp": "_Hp", 
                         "_Low": "_High", 
                         "_LP": "_HP", 
                         "_LOW": "_HIGH",
                         "_lP": "_hp",
                         "_LoW": "_high",
                         "_lOw": "_high"}

        for suffix, replacement in naming_values.items():
            if suffix in active_name:
                has_suffix = True
                head, body, tail = active_name.rpartition(suffix)
                new_name = head + replacement + tail
                break

        if has_suffix:
            if multiple_inactive == False:
                inactive_objs[0].name = new_name
            else:
                for idx, obj in enumerate(inactive_objs):
                    obj.name=new_name+f"_{idx:02d}"
        

        if has_suffix == False:
            if multiple_inactive == False:
                inactive_objs[0].name = active_obj.name + "_high"
                active_obj.name = active_obj.name + "_low"
            else:
                for idx, obj in enumerate(inactive_objs):
                    obj.name=inactive_objs[idx].name = active_obj.name+f"_high_{idx:02d}"
                active_obj.name = active_obj.name + "_low"

        return {'FINISHED'}








#COLLISION TOOLS



class hideUCX(bpy.types.Operator):
	bl_idname = "object.lr_hide_ucx"
	bl_label = "Hides all UCX objects"

	# @classmethod
	# def poll(cls, context): 
	# 	return context.mode == 'OBJECT'
		
	def execute(self, context):
		num = 0
		for i in bpy.data.objects:
			if 'UCX_' in i.name:
				i.hide_set(True)
				num += 1

		self.report({'INFO'}, f'{num} collisions hidden.')
		return {'FINISHED'}		
	
class unhideUCX(bpy.types.Operator):
	
	bl_idname = "object.lr_unhide_ucx"
	bl_label = "Unhides all UCX objects"
	
	# @classmethod
	# def poll(cls, context): 
	# 	return context.mode == 'OBJECT'

	def execute(self, context):
		num = 0
		for i in bpy.data.objects:
			if 'UCX_' in i.name:
				i.hide_set(False)
				num += 1

		self.report({'INFO'}, f'{num} collisions unhidden.')
		return {'FINISHED'}	   

class OBJECT_OT_NameUCX(bpy.types.Operator):
    '''Names collision meshes after active mesh. Select collisions then main mesh'''
    bl_idname = "object.lr_name_ucx"
    bl_label = "Names collision objects after active object"
    bl_options = {'REGISTER', 'UNDO'}	

    @classmethod
    def poll(cls, context): 
        return context.mode == 'OBJECT'

    def execute(self, context):

        selobj = bpy.context.selected_objects
        activeobj = bpy.context.object
        inactive_objs = []

        for obj in selobj:
            if obj != activeobj:
                inactive_objs.append(obj)

        # active_object_name = activeobj.name
        # matching_inactive_objs = {}
        # for inactive_obj in inactive_objs:
        #     if inactive_obj.startswith(f"UCX_{active_object_name}"):
        #         parts = inactive_obj.rsplit("_",1)
        #         if len(parts) == 2 and parts[1].isdigit():
        #             matching_inactive_objs.setdefault(int(parts[1]), []).append(inactive_obj)
        
    
        
        for count, obj in enumerate(inactive_objs):
            #Formats with one leading zero
            obj.name = f'UCX_{activeobj.name}_{count:02d}'
            obj.data.name = f'DATA_UCX_{activeobj.name}_{count:02d}'

        return {'FINISHED'}	   

class OBJECT_OT_selectObjectCollisions(bpy.types.Operator):
    '''Selects UCX_, UBX_, USP_, UCP_ collisions.\n1.Mesh selection - collision objects based on mesh name are selected \n2.Collision object selection - selects all other collisions belonging to the same object\n3.Empty object selection - All children objects with collision prefix is selected'''
    bl_idname = "object.lr_select_obj_collisions"
    bl_label = "Selects all object collisions"
    bl_options = {'REGISTER', 'UNDO'}	

    @classmethod
    def poll(cls, context): 
        return context.mode == 'OBJECT'

    def execute(self, context):
        collision_prefixes = set(["UCX_","UBX_","USP_","UCP_"])
        activeobj = bpy.context.object
        active_name = activeobj.name


        if activeobj.type == "MESH":        
            if active_name[:4] in collision_prefixes:
                parts = active_name.rsplit("_",1)
                if len(parts) > 0 and parts[1].isdigit():
                    active_name = parts[0][4:]    

            if activeobj is None:
                self.report({'WARNING'}, "No active object selected")
                return {'CANCELLED'}
            
            found_ubx = []
            found_ucp = []
            found_usp = []
            found_ucx = []

            for obj in context.scene.objects:
                if obj.type != "MESH":
                    continue
                
                obj_name = obj.name
                if obj_name.startswith(f"UCX_{active_name}"):
                    found_ucx.append(obj)
                elif obj_name.startswith(f"UBX_{active_name}"):
                    found_ubx.append(obj)
                elif obj_name.startswith(f"USP_{active_name}"):
                    found_usp.append(obj)
                elif obj_name.startswith(f"UCP_{active_name}"):
                    found_ucp.append(obj)


            all_collisions = found_ucx + found_ucp + found_usp + found_ubx

            if len(all_collisions) > 0:
                bpy.ops.object.select_all(action='DESELECT')
                for obj in all_collisions:
                    obj.select_set(True)
                bpy.context.view_layer.objects.active = all_collisions[0]
            else:
                self.report({"INFO"}, "Object has no matching collisions")

        if activeobj.type == "EMPTY":
            children_objs = activeobj.children_recursive
            collision_objs = []
            for obj in children_objs:
                  if obj.name[:4] in collision_prefixes:
                        collision_objs.append(obj)
                        # obj.select_set(True)
            
            if collision_objs:
                bpy.ops.object.select_all(action='DESELECT')
                for obj in collision_objs:
                    obj.select_set(True)
                bpy.context.view_layer.objects.active = collision_objs[0]

        return {'FINISHED'}	   





class hide_unhide_lattice(bpy.types.Operator):
	bl_idname = "object.lr_hide_unhide_lattice"
	bl_label = "Hides all Lattice objects"
	bl_options = {'REGISTER', 'UNDO'}

	# @classmethod
	# def poll(cls, context): 
	# 	return context.mode == 'OBJECT'
	
	#Property
	hide_lattice: bpy.props.BoolProperty(name = 'Hide Lattice', description = 'Hides lattice objects', default = False)
    
	def execute(self, context):
		for object in bpy.data.objects:
			if object.type == 'LATTICE':
				if self.hide_lattice == True:
					object.hide_set(True)
				elif self.hide_lattice == False:
					object.hide_set(False)

		return {'FINISHED'}		












