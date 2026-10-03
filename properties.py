import bpy
from bpy.props import FloatVectorProperty


class lr_tool_settings(bpy.types.PropertyGroup):
    uv_map_new_name: bpy.props.StringProperty(name="  Name", description="Name of the new UV set on selected", default="UVMask", maxlen=1024,)# type: ignore
    name_to_uv_index_set: bpy.props.StringProperty(name="  Name", description="Set uv index by name", default="UVMask", maxlen=1024,)# type: ignore
    uv_map_rename: bpy.props.StringProperty(name="  To", description="Rename uv on selected objects", default="New Name", maxlen=1024,)# type: ignore
    uv_map_delete_by_name: bpy.props.StringProperty(name="  Name", description="Name of the UV Map to delete on selected objects", default="UV Name", maxlen=1024,)# type: ignore
    select_uv_index: bpy.props.IntProperty(name="  Index", description="UV Map index to set active on selected objects", default=1, min = 1, soft_max = 5)# type: ignore
    remove_uv_index: bpy.props.IntProperty(name="Index to remove", description="UV Map index to remove on selected objects", default=1, min = 1, soft_max = 5)# type: ignore
    vertex_color_offset_amount: bpy.props.FloatProperty(name="Offset amount", default=0.1, min = 0, max = 1)# type: ignore
    lr_vc_swatch: FloatVectorProperty(name="object_color",subtype='COLOR',default=(1.0, 1.0, 1.0),min=0.0, max=1.0,description="color picker")# type: ignore

    lr_vc_alpha_swatch: bpy.props.FloatProperty(name="Alpha Value", step = 5, default=0.5, min = 0, max = 1)# type: ignore

    hide_by_name: bpy.props.StringProperty(name="", description="Hide objects with this name", default="UCX_", maxlen=1024,)# type: ignore
    unhide_by_name: bpy.props.StringProperty(name="", description="Unhide objects with this name", default="UCX", maxlen=1024,)# type: ignore
    
    vc_write_to_red: bpy.props.BoolProperty(name="Set R", description="False: Red channel won't be affected.", default=True)# type: ignore
    vc_write_to_green: bpy.props.BoolProperty(name="Set G", description="False: Green channel won't be affected.", default=True)# type: ignore
    vc_write_to_blue: bpy.props.BoolProperty(name="Set B", description="False: Blue channel won't be affected.", default=True)# type: ignore

    uv_copy_paste_destination: bpy.props.IntProperty(name="Destination Index", description="Paste UVs destination index", default=2, min = 1, soft_max = 7) # type: ignore


class lr_tool_settings_object(bpy.types.PropertyGroup):
    lr_object_info_index: bpy.props.IntProperty(default=0)# type: ignore
    
    

    def update_obj_info_attr(self,context):
        if context.object:
            print(self['lr_object_info_index'])
            # self['lr_object_info_index']=2
            # row.prop(context.object,'lr_object_info_index')

