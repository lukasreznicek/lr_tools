import bpy


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
    
class nameUCX(bpy.types.Operator):
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
		inactive_obj = []
		for obj in selobj:
			if obj != activeobj:
				inactive_obj.append(obj)

		
		for count, obj in enumerate(inactive_obj):
			#Formats with one leading zero
			obj.name = f'UCX_{activeobj.name}_{count:02d}'
			obj.data.name = f'DATA_UCX_{activeobj.name}_{count:02d}'
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











