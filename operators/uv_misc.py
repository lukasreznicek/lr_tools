
import bpy
import bmesh
import math
from bpy.types import Menu
from bpy.types import Operator
from bpy.props import BoolProperty
from itertools import product
from collections import defaultdict


class OBJECT_OT_lr_uv_map_by_index_custom(bpy.types.Operator):
	'''Set UV Map by index on selected objects. '''
	bl_idname = "object.lr_uv_map_by_index_custom"
	bl_label = "Set UV index on selected objects."
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):

		uv_index_custom = bpy.context.scene.lr_tools.select_uv_index



		for obj in bpy.context.selected_objects:
			if obj.type == 'MESH':
				
				uv_layer_amount = len(obj.data.uv_layers)
				
				if uv_index_custom <= uv_layer_amount:
					obj.data.uv_layers.active_index = uv_index_custom-1
				else:
					self.report({'INFO'}, 'Skipping: '+obj.name+', has no uv map with index: '+str(uv_index_custom))
		return {'FINISHED'}		


class OBJECT_OT_lr_uv_map_by_index(bpy.types.Operator):
	'''Set UV Map by index on selected objects.'''
	bl_idname = "object.lr_uv_map_by_index"
	bl_label = "Set UV index on selected objects."
	bl_options = {'REGISTER', 'UNDO'}
	uv_index: bpy.props.IntProperty(name='UV Index', description='', default=1, min=1, max=10, step=1)

	def execute(self, context):
		for obj in bpy.context.selected_objects:
			if obj.type == 'MESH':
				
				uv_layer_amount = len(obj.data.uv_layers)
				
				if self.uv_index <= uv_layer_amount:
					obj.data.uv_layers.active_index = self.uv_index-1
				else:
					self.report({'INFO'}, 'Skipping: '+obj.name+', has no uv map with index: '+str(self.uv_index))

		return {'FINISHED'}		


class UVIndexName(bpy.types.Operator):
	'''Set UV Map by name on selected objects'''
	bl_idname = "object.lr_uv_index_name"
	bl_label = "Set UV index by name"
	def execute(self, context):

		data = []
		for i in bpy.context.selected_objects:
			if i.type == 'MESH':
				data.append(i.data)
		data = list(dict.fromkeys(data))
		


		for obj in data:
			
			#Number of UV layers
			uv_amount = len(obj.uv_layers)

			#Create list of object uv names
			uv_names = []
			for uv in range(uv_amount):
				uv_names.append(obj.uv_layers[uv].name)

			if bpy.context.scene.lr_tools.name_to_uv_index_set in uv_names:
				indextouvset = uv_names.index(bpy.context.scene.lr_tools.name_to_uv_index_set)
				obj.uv_layers.active_index = indextouvset

			else:
				self.report({'INFO'}, 'Mesh: '+obj.name+', does not have "'+bpy.context.scene.lr_tools.name_to_uv_index_set+'" UVMap.')



		return {'FINISHED'}		


class NewUVSet(bpy.types.Operator):
	'''New UV map on selected objects'''
	bl_idname = "object.lr_new_uv_set"
	bl_label = "New UV map Bake on selected objects"

	def execute(self, context):
		#Exclude duplicated meshes
		data = []
		for i in bpy.context.selected_objects:
			if i.type == 'MESH':
				data.append(i.data)
		data = list(dict.fromkeys(data))
		
		
		uv_names = []
		print(data)

		for obj in data:
			
			#Number of UV layers
			uv_amount = len(obj.uv_layers)

			#Create list of object uv names
			uv_names = []
			for uv in range(uv_amount):
				uv_names.append(obj.uv_layers[uv].name)


			if  bpy.context.scene.lr_tools.uv_map_new_name in uv_names:
				self.report({'INFO'}, 'Not adding new UVMap to mesh: '+obj.name+', already has UVMap with this name. ('+bpy.context.scene.lr_tools.uv_map_new_name+')')
				pass

			else:
				obj.uv_layers.new(name=bpy.context.scene.lr_tools.uv_map_new_name)

					
				 
				 
				 
				 

		return {'FINISHED'}		


class RemoveActiveUVSet(bpy.types.Operator):
	'''Remove active UV map on selected objects'''
	bl_idname = "object.lr_remove_active_uv_set"
	bl_label = "Remove active UV map on selected objects"
	
	def execute(self, context):


		#Exclude duplicated meshes
		objdata = []
		for i in bpy.context.selected_objects:
			if i.type == 'MESH':
				objdata.append(i.data)
		objdata = list(dict.fromkeys(objdata))




		for obj in objdata:
			uv_amount = len(obj.uv_layers)-1
			act_index = obj.uv_layers.active_index

			if uv_amount == -1:
				pass

			elif act_index <= uv_amount:
				UVName = obj.uv_layers.active.name
				obj.uv_layers.remove(obj.uv_layers.get(UVName))
	
			else:
				pass

				
				
		return {'FINISHED'}		


class OBJECT_OT_remove_uv_by_index(bpy.types.Operator):
	'''Remove UV Set by index. Index starts from 1.'''
	bl_idname = "object.lr_remove_uv_set_by_index"
	bl_label = "Remove UV Map by index. Index starts from 1."
	bl_options = {'REGISTER', 'UNDO'}
	
	uv_index: bpy.props.IntProperty(name='UV Index', description='', default=1, min=1, max=10, step=1)
	
	def execute(self, context):
		
		#uv_index = bpy.context.scene.lr_tools.remove_uv_index
		#Exclude duplicated meshes
		objdata = []
		for i in bpy.context.selected_objects:
			if i.type == 'MESH':
				objdata.append(i.data)
		objdata = list(dict.fromkeys(objdata))


		for obj in objdata:
			uv_amount = len(obj.uv_layers)
			

			if  uv_amount >= self.uv_index:
				#UVIndex = obj.uv_layers[self.uv_index]
				obj.uv_layers.remove(obj.uv_layers[self.uv_index-1])


		bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1) #Redraw UI

		return {'FINISHED'}		


class RenameActiveUVSet(bpy.types.Operator):
	'''Renames active UV Map on selected objects'''
	bl_idname = "object.lr_rename_active_uv_set"
	bl_label = "Renames active UV Map on selected objects"
	def execute(self, context):


		#Exclude duplicated meshes
		objdata = []
		for i in bpy.context.selected_objects:
			if i.type == 'MESH':
				objdata.append(i.data)
		objdata = list(dict.fromkeys(objdata))


		for obj in objdata:
			obj.uv_layers.active.name = bpy.context.scene.lr_tools.uv_map_rename
			
		return {'FINISHED'}			
	

class lr_replaceobjects(bpy.types.Operator):
	"""Replaces inactive objects from active with parents"""
	bl_idname = "object.lr_replace_objects"
	bl_label = "Replace objects. Active to inactive(LR Tools)"
	
	@classmethod
	def poll(cls, context):
		return context.mode == 'OBJECT'


	def execute(self, context):

		#Main variables		
		act = bpy.context.active_object
		selected = bpy.context.selected_objects
		ina = selected.copy()
		ina.remove(act)
		ina_number = len(ina)
		
		new = []
		fordelete = []
		for obj in range(0,ina_number):
			new_obj = act.copy()
			bpy.context.scene.collection.objects.link(new_obj)
			new.append(new_obj)


		for a,b in zip(ina,new):
			#Update parents	
			if a.parent:
				parent = a.parent
				a.parent = None
				b.parent = parent
			else:
				print('Does not have a parent') 
			#Match locations
			matrix =  a.matrix_world
			#b.location = a.location
			#b.scale = a.scale
			#b.rotation_euler = a.rotation_euler			
			b.matrix_world = matrix
			b_name = a.name
			a.name = "TemporaryForDelete"
			fordelete.append(a)
			b.name = b_name		


		#Update children		
			if a.children:
				print('preforming child relinking')
				
				childrenparent = []
				childrenparent.append(b)
				print('Reparenting to:', childrenparent[0])
				
				
				children = []
				for obj in a.children:
					children.append(obj)
				print('Children object being relinked:', children)
			
				
				for obj in children:
					child_matrix = obj.matrix_world
					obj.parent = None
					obj.parent = childrenparent[0]
					obj.matrix_world = child_matrix
					
			else:
				print('Object has no children')			
			
		bpy.ops.object.delete({"selected_objects": fordelete})
		 
		return {'FINISHED'}			


class move_uv_map_up(bpy.types.Operator):
	'''Moves active UV Map one index up on selected objects'''
	bl_idname = "object.mono_move_uv_map_up"
	bl_label = "Moves active UV Map one index up on selected objects"
	def execute(self, context):

		#Exclude duplicated meshes
		objdata = []
		for i in bpy.context.selected_objects:
			if i.type == 'MESH':
				objdata.append(i.data)
		objdata = list(dict.fromkeys(objdata))





		def move_up(objdata):
			act_index = objdata.uv_layers.active_index
			if act_index > 0:      
				act_index_name = objdata.uv_layers.active.name
				up_index = act_index-1
				name_up = objdata.uv_layers[act_index-1].name

				bm = bmesh.new()
				bm.from_mesh(objdata)
				bm.loops.layers.uv.new('temp')

				bm.loops.layers.uv['temp'].copy_from(bm.loops.layers.uv[name_up])
				bm.loops.layers.uv[name_up].copy_from(bm.loops.layers.uv[act_index_name])
				bm.loops.layers.uv[act_index_name].copy_from(bm.loops.layers.uv['temp'])



				bm.to_mesh(objdata)
				#Update data
				objdata.update()

		        #switch names
				objdata.uv_layers[up_index].name = 'temp_up'
				objdata.uv_layers[act_index].name = name_up
				objdata.uv_layers[up_index].name = act_index_name
				#Remove temp
				objdata.uv_layers.remove(objdata.uv_layers['temp'])
				#Set active index
				objdata.uv_layers.active_index = up_index
			else:
				pass

		act_index = objdata[0].uv_layers.active_index
		for i in objdata:
			if	len(i.uv_layers) != 1:
				# Skip if active index is already up
				if 	i.uv_layers.active_index != 0:
					if i.uv_layers.active_index != act_index:
						move_up(i)
						self.report({'WARNING'}, 'Completed but objects did not have the same active index')

					elif i.uv_layers.active_index == act_index:
						move_up(i)
						self.report({'INFO'}, 'UV moved up')
				else:
					self.report({'INFO'}, 'Skipped: UV already up')
			else:
				self.report({'INFO'}, 'Skipped: Only one UV map')


		return {'FINISHED'}	


class move_uv_map_down(bpy.types.Operator):
	'''Moves active UV Map one index down on selected objects'''
	bl_idname = "object.mono_move_uv_map_down"
	bl_label = "Moves active UV Map one index down on selected objects"
	def execute(self, context):



		#Exclude duplicated meshes
		objdata = []
		for i in bpy.context.selected_objects:
			if i.type == 'MESH':
				objdata.append(i.data)
		objdata = list(dict.fromkeys(objdata))


		def move_down(objdata):

			act_index = objdata.uv_layers.active_index
			if act_index < len(objdata.uv_layers)-1:
				act_index_name = objdata.uv_layers.active.name
				down_index = act_index+1
				name_down = objdata.uv_layers[act_index+1].name

				bm = bmesh.new()
				bm.from_mesh(objdata)
				bm.loops.layers.uv.new('temp')

				bm.loops.layers.uv['temp'].copy_from(bm.loops.layers.uv[name_down])
				bm.loops.layers.uv[name_down].copy_from(bm.loops.layers.uv[act_index_name])
				bm.loops.layers.uv[act_index_name].copy_from(bm.loops.layers.uv['temp'])



				bm.to_mesh(objdata)
				#Update data
				objdata.update()

				#switch names
				objdata.uv_layers[down_index].name = 'temp_up'
				objdata.uv_layers[act_index].name = name_down
				objdata.uv_layers[down_index].name = act_index_name
				#Remove temp
				objdata.uv_layers.remove(objdata.uv_layers['temp'])
				#Set active index
				objdata.uv_layers.active_index = down_index
			else:
				print('skipping')  

			
		act_index = objdata[0].uv_layers.active_index
		for i in objdata:
			if	len(i.uv_layers) != 1:
				if 	i.uv_layers.active_index != len(i.uv_layers)-1:
					if i.uv_layers.active_index != act_index:
						move_down(i)
						self.report({'WARNING'}, 'Completed but objects did not have the same active index')

					elif i.uv_layers.active_index == act_index:
						move_down(i)
						self.report({'INFO'}, 'UV moved down')
				else:
					self.report({'INFO'}, 'Skipped: UV already down')
			else:
				self.report({'INFO'}, 'Skipped: Only one UV map')

		return {'FINISHED'}	


class lr_remove_uv_by_name(bpy.types.Operator):
	'''Removes UV Map by name on selected objects'''
	bl_idname = "object.lr_remove_uv_by_name"
	bl_label = "Removes UV Map by name on selected objects"
	
	
	def execute(self, context):
		selected_objects = bpy.context.selected_objects

		uv_layer_name = bpy.context.scene.lr_tools.uv_map_delete_by_name

	
		for obj in selected_objects:
			if obj.type == 'MESH':
				if uv_layer_name in obj.data.uv_layers:
					obj.data.uv_layers.remove(obj.data.uv_layers[uv_layer_name])
		
		self.report({'INFO'}, 'Done')
		return {'FINISHED'}	


class lr_randomize_uv_offset(bpy.types.Operator):
	'''UVWarp modifier offset randomizator. Modifier must be named UVWarp_S. Select objects and run.'''
	bl_idname = "object.lr_randomize_uv_offset"
	bl_label = "Randomizes UV Offset on all objects with UVWarp modifier."
	
	
	def execute(self, context):

		#Determine appropriate amount of numbers needed
		object_squared = math.ceil(math.sqrt(len(bpy.context.selected_objects)))

		#Create list for possible combination list generation
		init_numb = 0
		items = []
		for n in range(object_squared):
			items.append(init_numb)
			init_numb+=1

		#Generate combinations 
		combinations = []
		for item in product(items, repeat=2):
			combinations.append(item)

		#Modifier must be named UVWarp_S in order for this script to work
		count = 0
		for object in bpy.context.selected_objects:
			for modifier in object.modifiers:
				if modifier.name =='UVWarp_S' and modifier.type == 'UV_WARP':
					modifier.offset[0] = combinations[count][0]
					modifier.offset[1] = combinations[count][1]
					count +=1
					
		return {'FINISHED'}	


class lr_grid_redistribute_uv_islands(bpy.types.Operator):
	'''Redistribute UV islands to grid'''
	bl_idname = "object.lr_grid_redistribute_uv_islands"
	bl_label = "Redistribute UV islands to grid"
	
	
	def execute(self, context):

		__face_to_verts = defaultdict(set)
		__vert_to_faces = defaultdict(set)

		obj = bpy.context.active_object
		bm = bmesh.from_edit_mesh(obj.data)
		uv_layer = bm.loops.layers.uv.verify()

		selected_faces = [f for f in bm.faces if f.select]

		def __parse_island(bm, face_idx, faces_left, island):
			if face_idx in faces_left:
				faces_left.remove(face_idx)
				island.append({'face': bm.faces[face_idx]})
				for v in __face_to_verts[face_idx]:
					connected_faces = __vert_to_faces[v]
					if connected_faces:
						for cf in connected_faces:
							__parse_island(bm, cf, faces_left, island)

		def __get_island(bm):
			uv_island_lists = []
			faces_left = set(__face_to_verts.keys())
			while len(faces_left) > 0:
				current_island = []
				face_idx = list(faces_left)[0]
				__parse_island(bm, face_idx, faces_left, current_island)
				uv_island_lists.append(current_island)
			return uv_island_lists

		for f in selected_faces:
			for l in f.loops:
				id = l[uv_layer].uv.to_tuple(5), l.vert.index
				__face_to_verts[f.index].add(id)
				__vert_to_faces[id].add(f.index)

		#Dictionary
		uv_island_lists = __get_island(bm)

		# ---
		#Determine appropriate amount of numbers needed
		object_squared = math.ceil(math.sqrt(len(uv_island_lists)))

		#Create list for possible combination list generation
		init_numb = 0
		items = []
		for n in range(object_squared):
			items.append(init_numb)
			init_numb+=1

		#Generate combinations 
		combinations = []
		for item in product(items, repeat=2):
			combinations.append(item)
		# ---
		uvmap = bm.loops.layers.uv.active
		count = 0
		for island in uv_island_lists:
			for faces in island:
				for loop in faces['face'].loops:
					loop[uvmap].uv[0]+=combinations[count][0]
					loop[uvmap].uv[1]+=combinations[count][1]
			count+=1
	
		bmesh.update_edit_mesh(obj.data)

		return {'FINISHED'}	
	



class LR_Tools_OT_UVCopyPaste(bpy.types.Operator):
	'''For copying UVs from one UVmap to another on the same object.\nSelect UVs to copy and run operator. UVMap will be added if missing.\n\nTo separate island and move, select vertices with Disabled 'Sticky Selection Mode' in UV window'''
	bl_idname = "lr_tools.uv_copy_paste"
	bl_label = "Copy selected UVs in active index to target index"
	bl_options = {'REGISTER', 'UNDO'}

	uv_index_destination: bpy.props.IntProperty(name='Target UV Channel', description='Starting from 1.', default=1, min=1, max=10, step=1)

	def execute(self, context):
		selected_objects = bpy.context.selected_objects
		uv_index_destination = self.uv_index_destination-1
		for obj in selected_objects:
			if obj.type !='MESH':
				continue

			bm = bmesh.from_edit_mesh(obj.data)



			# if  uv_index_destination > uv_layer_amount:
			# 	return {'FINISHED'}
			while uv_index_destination > len(bm.loops.layers.uv)-1:
				bm.loops.layers.uv.new('UVMap')

			uv_layer_source = bm.loops.layers.uv.active
			uv_layer_destination = bm.loops.layers.uv[uv_index_destination]

			# Get selected UV loops and transfer UV coordinates
			for vert in bm.verts:
				for loop in vert.link_loops:
					if loop[uv_layer_source].select:
						loop[uv_layer_destination].uv = loop[uv_layer_source].uv

			bmesh.update_edit_mesh(obj.data)
		return {'FINISHED'}
		

class LR_TOOLS_OT_uv_offset_by_object_id(bpy.types.Operator):
	'''Select multiple objects and run the operator. UVs for each object will be moved into unique V index'''
	
	bl_idname = "lr_tools.uv_offset_by_object_id"
	bl_label = "Offsets objects UVs in V axis. Each object will have its loops in its own UV space."
	bl_options = {'REGISTER', 'UNDO'}
    
	@classmethod
	def poll(cls, context):
		# Check if the operator can run in the current context
		return context.mode == 'OBJECT'    

	def execute(self, context):

		for id,obj in enumerate(bpy.context.selected_objects):
			move_UVs(obj,0,id)

		return {'FINISHED'}

	
def move_UVs(obj, u_offset, v_offset):

    if obj.type ==  'MESH': 
        uv_layer = obj.data.uv_layers.active.data
        for loop in obj.data.loops:
            uv_coords = uv_layer[loop.index].uv
            uv_coords[0] += u_offset
            uv_coords[1] += v_offset