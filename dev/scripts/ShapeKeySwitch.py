"""Switches shape key on multiple objects"""
import bpy
#Switch Shape key on multiple
for obj in bpy.context.selected_objects:
    if obj.type != "MESH":
        continue
    obj.active_shape_key_index = 0
