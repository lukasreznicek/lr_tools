# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "LR Tools",
    "author" : "Lukas Reznicek",
    "description" : "Set of tools for workflow simplification",
    "blender" : (2, 82, 0),
    "version" : (1, 1, 0),
    "location" : "",
    "warning" : "",
    "category" : "UV"
}

import bpy, os, bmesh, subprocess

from .operators.attributes import OBJECT_OT_lr_add_attribute,OBJECT_OT_lr_remove_attribute
from .operators.unwrap_in_place import LR_Unwrap
# from .operators.export import lr_export_but_one_material,lr_exportformask
from .operators.set_vertex_color import OBJECT_OT_lr_assign_vertex_color,lr_offset_vertex_color,lr_pick_vertex_color
from .operators.set_vertex_alpha import lr_vertex_rgb_to_alpha
from .operators.select import lr_select_obj_by_topology,lr_deselect_duplicate
from .operators.replace_children import lr_replace_children
from .operators.sculpt import lr_multires_sculpt_offset
from .operators.object_drop import OBJECT_OT_lr_drop_object



from .operators import UCX
from .operators import uv_misc
from .operators import mesh_misc
from .operators import window_management

from bpy.types import Panel, UIList
from bpy.props import IntProperty, CollectionProperty, StringProperty,FloatVectorProperty,BoolProperty

from bpy.types import Menu
from bpy.types import Operator
from bpy.app.handlers import persistent
#For sub panels
from bl_ui.properties_object import ObjectButtonsPanel






# Preferences ------------------------------------------------------------------------------------------------------------------------------            
class AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__
                                    
    def draw(self, context):
        # Search for keymap items in the addon's keymap list (addon_keymaps) from within Blender settings and display the menu

        import rna_keymap_ui 

        layout = self.layout
        box = layout.box()
        color = box.column()
        color.label(text="Keymap List:",icon="KEYINGSET")


        wm = bpy.context.window_manager
        kc = wm.keyconfigs.user
        old_km_name = ""
        get_kmi_l = []
        for km_add, kmi_add in addon_keymaps:
            for km_con in kc.keymaps:
                if km_add.name == km_con.name:
                    km = km_con
                    break   

            for kmi_con in km.keymap_items:
                if kmi_add.idname == kmi_con.idname:
                    if kmi_add.name == kmi_con.name:
                        get_kmi_l.append((km,kmi_con))

        get_kmi_l = sorted(set(get_kmi_l), key=get_kmi_l.index)

        for km, kmi in get_kmi_l:
            if not km.name == old_km_name:
                color.label(text=str(km.name),icon="DOT")
            color.context_pointer_set("keymap", km)
            rna_keymap_ui.draw_kmi([], kc, km, kmi, color, 0)
            color.separator()
            old_km_name = km.name
# END Preferences ------------------------------------------------------------------------------------------------------------------------------  


#Keymaps ---------------------------------------------------------------------------------------------------------------------------------------
addon_keymaps = []
def register_keymaps():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='UV Editor', space_type= 'EMPTY')
        kmi = km.keymap_items.new('uv.lr_unwrap', type= 'X', value='PRESS', shift=True, ctrl=True, alt=False)
        addon_keymaps.append((km, kmi))

        # km = kc.keymaps.new(name='UV Editor', space_type= 'EMPTY')
        # kmi = km.keymap_items.new('uv.lr_unwrap2', type= 'X', value='PRESS', shift=True, ctrl=True, alt=False)
        # addon_keymaps.append((km, kmi))


        km = kc.keymaps.new(name='Sculpt', space_type= 'EMPTY')
        kmi = km.keymap_items.new('lr.offset_multires_sculpt_subd', type= 'D', value='PRESS', shift=True, ctrl=False, alt=False)
        kmi.properties.decrease = True
        addon_keymaps.append((km, kmi))
        
        km = kc.keymaps.new(name='Sculpt', space_type= 'EMPTY')
        kmi = km.keymap_items.new('lr.offset_multires_sculpt_subd', type= 'D', value='PRESS', shift=False, ctrl=False, alt=False)
        kmi.properties.decrease = False
        addon_keymaps.append((km, kmi))


def unregister_keymaps():

    for km,kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

#END Keymaps  ---------------------------------------------------------------------------------------------------------------------------------

# Properties 
# To acess properties: bpy.data.scenes['Scene'].lr_tools
# Is assigned by pointer property below in class registration.



class lr_tool_settings(bpy.types.PropertyGroup):
    uv_map_new_name: bpy.props.StringProperty(name="  Name", description="Name of the new UV set on selected", default="UVMask", maxlen=1024,)
    name_to_uv_index_set: bpy.props.StringProperty(name="  Name", description="Set uv index by name", default="UVMask", maxlen=1024,)
    uv_map_rename: bpy.props.StringProperty(name="  To", description="Rename uv on selected objects", default="New Name", maxlen=1024,)
    uv_map_delete_by_name: bpy.props.StringProperty(name="  Name", description="Name of the UV Map to delete on selected objects", default="UV Name", maxlen=1024,)
    select_uv_index: bpy.props.IntProperty(name="  Index", description="UV Map index to set active on selected objects", default=1, min = 1, soft_max = 5)
    remove_uv_index: bpy.props.IntProperty(name="Index to remove", description="UV Map index to remove on selected objects", default=1, min = 1, soft_max = 5)
    vertex_color_offset_amount: bpy.props.FloatProperty(name="Offset amount", default=0.1, min = 0, max = 1)
    lr_vc_swatch: FloatVectorProperty(name="object_color",subtype='COLOR',default=(1.0, 1.0, 1.0),min=0.0, max=1.0,description="color picker")
    lr_vc_alpha_swatch: bpy.props.FloatProperty(name="Alpha Value", step = 5, default=0.5, min = 0, max = 1)

    hide_by_name: bpy.props.StringProperty(name="", description="Hide objects with this name", default="UCX_", maxlen=1024,)
    unhide_by_name: bpy.props.StringProperty(name="", description="Unhide objects with this name", default="UCX", maxlen=1024,)
    
    vc_write_to_red: bpy.props.BoolProperty(name="Set R", description="False: Red channel won't be affected.", default=True)
    vc_write_to_green: bpy.props.BoolProperty(name="Set G", description="False: Green channel won't be affected.", default=True)
    vc_write_to_blue: bpy.props.BoolProperty(name="Set B", description="False: Blue channel won't be affected.", default=True)


    # # Enum for hiding and unhiding objects
    # hide_objs:bpy.props.EnumProperty(
    #     name = 'Hide Obj',
    #     items=[
    #         ("object.lr_hide_object", "Cube", '', 'HIDE_ON', 0),
    #         ("mesh.primitive_cube_add", "Cube", '', 'HIDE_ON', 1),
    #         ("mesh.primitive_circle_add", "Circle", '', 'HIDE_ON', 2),
    #         ("mesh.primitive_uv_sphere_add", "UV Sphere", '', 'HIDE_ON', 3),
    #     ],
    #     description="offers....",
    #     #default="mesh.primitive_circle_add",
    #     update=execute_hide_operator
    # )

    # unhide_objs:bpy.props.EnumProperty(
    #     name = 'Show Obj',
    #     items=[
    #         ("mesh.primitive_plane_add", "Plane", '', 'MESH_PLANE', 0),
    #         ("mesh.primitive_cube_add", "Cube", '', 'MESH_CUBE', 1),
    #         ("mesh.primitive_circle_add", "Circle", '', 'MESH_CIRCLE', 2),
    #         ("mesh.primitive_uv_sphere_add", "UV Sphere", '', 'MESH_UVSPHERE', 3),
    #     ],
    #     description="offers....",
    #     #default="mesh.primitive_plane_add",
    #     update=execute_unhide_operator
    # )

#UI -------------------------------------------------------------------------------------
class VIEW3D_PT_lr_vertex(bpy.types.Panel):
    bl_label = "VERTEX COLOR"
    bl_idname = "OBJECT_PT_lr_vertex"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'LR'

    def draw(self, context):
        lr_tools = context.scene.lr_tools
        settings_l = bpy.context.tool_settings.image_paint        

        active_brush = settings_l.brush 
         


        #Palette colors
        if context.mode == 'OBJECT':
            layout3  = self.layout.box()
            layout3.template_ID(settings_l, "palette", new="palette.new")
            if settings_l.palette:
                layout3.template_palette(settings_l, "palette", color=True)
            

        layout_a = self.layout.box()
        

        #Set RGB operators
        column = layout_a.column(align=True)
        column.label(text='RGB')
        
        row = layout_a.row(align=True)
        row.prop(lr_tools, "vc_write_to_red")
        row.prop(lr_tools, "vc_write_to_green")
        row.prop(lr_tools, "vc_write_to_blue")

        column_row = column.row(align=True)
        column_row.prop(active_brush, 'color', text="")
        
        rgb_picker = column_row.operator("lr.pick_vertex_color", icon='EYEDROPPER', text="")  
        rgb_picker.pick_alpha = False
        column = layout_a.column(align=True)
        

        #!!! operator_prop['color_r']  this type of assignment needs to be here because of the property update parameter.Does not trigger property update. 
        # operator_prop.color_r this assignment will trigger update and it will constantly loop.

        column_row = column.row(align=True)
        operator_prop = column_row.operator("lr.assign_vertex_color", icon='PASTEDOWN', text="Set Color")
        operator_prop['color_r'] = active_brush.color[0]
        operator_prop['color_r_int'] = int(round(active_brush.color[0] * 255))

        operator_prop['color_g'] = active_brush.color[1]
        operator_prop['color_g_int'] = int(round(active_brush.color[1] * 255))

        operator_prop['color_b'] = active_brush.color[2]
        operator_prop['color_b_int'] = int(round(active_brush.color[2] * 255))


        #Whether to write into these channels
        operator_prop['set_r'] = lr_tools.vc_write_to_red
        operator_prop['set_g'] = lr_tools.vc_write_to_green
        operator_prop['set_b'] = lr_tools.vc_write_to_blue

        operator_prop = column_row.operator("lr.assign_vertex_color", icon='SEQUENCE_COLOR_01', text="")
        operator_prop['color_r'] = float(1.0)
        operator_prop['color_r_int'] = int(255)
        
        operator_prop['color_g'] = float(0)
        operator_prop['color_g_int'] = int(0)

        operator_prop['color_b'] = float(0)
        operator_prop['color_b_int'] = int(0)

        operator_prop = column_row.operator("lr.assign_vertex_color", icon='SEQUENCE_COLOR_04', text="")
        operator_prop['color_r'] = float(0)
        operator_prop['color_r_int'] = int(0)

        operator_prop['color_g'] = float(1)
        operator_prop['color_g_int'] = int(255)

        operator_prop['color_b'] = float(0)
        operator_prop['color_b_int'] = int(0)


        operator_prop = column_row.operator("lr.assign_vertex_color", icon='SEQUENCE_COLOR_05', text="")
        operator_prop['color_r'] = float(0)
        operator_prop['color_r_int'] = int(0)

        operator_prop['color_g'] = float(0)
        operator_prop['color_g_int'] = int(0)

        operator_prop['color_b'] = float(1)
        operator_prop['color_b_int'] = int(255)
        
        operator_prop = column_row.operator("lr.assign_vertex_color", icon='SEQUENCE_COLOR_09', text="")
        operator_prop['color_r'] = float(0)
        operator_prop['color_r_int'] = int(0)

        operator_prop['color_g'] = float(0)
        operator_prop['color_g_int'] = int(0)

        operator_prop['color_b'] = float(0)
        operator_prop['color_b_int'] = int(0)



        # #Offset operators
        # column_row = column.row(align=True)
        # column_row.operator("lr.offset_vertex_color", icon='TRIA_DOWN', text="").invert = True
        # column_row.operator("lr.offset_vertex_color", icon='TRIA_UP', text="").invert = False
        # column_row.prop(context.scene.lr_tools,'vertex_color_offset_amount')
        

        
        #Alpha operators
        
        column = layout_a.column(align=True)
        column.label(text='Alpha')
           
        column_row = column.row(align = True)
        column_row.prop(context.scene.lr_tools,'lr_vc_alpha_swatch')
        alpha_picker = column_row.operator("lr.pick_vertex_color", icon='EYEDROPPER', text="")  
        alpha_picker.pick_alpha = True



        props_a = column.operator("lr.assign_vertex_alpha", icon='PASTEDOWN', text="Set Alpha")
        props_a['color_a'] = bpy.context.scene.lr_tools.lr_vc_alpha_swatch
        props_a['color_a_int'] = int(round(bpy.context.scene.lr_tools.lr_vc_alpha_swatch * 255))

        '''
        column_row = column.row(align = True)
        props_a = column_row.operator("lr.assign_vertex_alpha",  text="0")
        props_a['color_a'] = 0
        props_a['color_a_int'] = int(0)

        props_a = column_row.operator("lr.assign_vertex_alpha",  text=".1")
        props_a['color_a'] = 0.1
        props_a['color_a_int'] = int(round(0.1*255))

        props_a = column_row.operator("lr.assign_vertex_alpha",  text=".2")
        props_a['color_a'] = 0.2
        props_a['color_a_int'] = int(round(0.2*255))

        props_a = column_row.operator("lr.assign_vertex_alpha",  text=".3")
        props_a['color_a'] = 0.3
        props_a['color_a_int'] = int(round(0.3*255))

        props_a = column_row.operator("lr.assign_vertex_alpha",  text=".4")
        props_a['color_a'] = 0.4
        props_a['color_a_int'] = int(round(0.4*255))

        props_a = column_row.operator("lr.assign_vertex_alpha",  text=".5")
        props_a['color_a'] = 0.5
        props_a['color_a_int'] = int(round(0.5*255))

        props_a = column_row.operator("lr.assign_vertex_alpha",  text=".6")
        props_a['color_a'] = 0.6
        props_a['color_a_int'] = int(round(0.6*255))

        props_a = column_row.operator("lr.assign_vertex_alpha",  text=".7")
        props_a['color_a'] = 0.7
        props_a['color_a_int'] = int(round(0.7*255))

        props_a = column_row.operator("lr.assign_vertex_alpha",  text=".8")
        props_a['color_a'] = 0.8
        props_a['color_a_int'] = int(round(0.8*255))

        props_a = column_row.operator("lr.assign_vertex_alpha",  text=".9")
        props_a['color_a'] = 0.9
        props_a['color_a_int'] = int(round(0.9*255))

        props_a = column_row.operator("lr.assign_vertex_alpha",  text="1")
        props_a['color_a'] = 1
        props_a['color_a_int'] = int(255)
        '''



class VIEW3D_PT_lr_object(bpy.types.Panel):
    bl_idname = "OBJECT_PT_lr_object"
    bl_label = "OBJECT"
    bl_options = {'DEFAULT_CLOSED'}
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "LR"
    #	bl_context = "object"

    # @classmethod
    # def poll(cls, context):
    #     return context.mode == 'OBJECT'

        
    def draw(self, context):
        lr_tools = context.scene.lr_tools
        

        layout = self.layout.box()
        layout.operator('lr.drop_object', text='Drop Obj', icon = 'TRIA_DOWN_BAR')
        
        
        
        layout = self.layout.box()
        
        layout.label(text="Replace references")
        row = layout.row(align=True)
        row.operator("object.lr_replace_objects", text="Object from active", icon = 'UV_SYNC_SELECT')
        row.operator("object.lr_replace_children", text="Children from active", icon ='MOD_ARRAY')
        row = layout.row(align=True)
        row.operator("object.lr_set_collection_offset_from_empty", text="Collection offset update", icon ='SEQ_SEQUENCER')
        


        layout = self.layout.box()
        layout.label(text="Select")
        layout.operator("object.lr_select_obj_by_topology", text="Topology", icon = 'MOD_WIREFRAME')
        layout.operator("object.lr_deselect_duplicate", text="Deselect duplicate", icon = 'GHOST_DISABLED')



        layout = self.layout.box()
        layout.label(text="Hide/Unhide")
        # layout.prop(lr_tools, "hide_objs")
        # layout.prop(lr_tools, "unhide_objs")


        row = layout.row(align=True)


        op = row.operator("object.lr_hide_object", text="Hide", icon = 'HIDE_ON')
        op.name = lr_tools.hide_by_name
        op.hide = True

        row.prop(lr_tools, "hide_by_name",icon_only=False)
        




        row = layout.row(align=True)
        op = row.operator("object.lr_hide_object", text="Unhide", icon ='HIDE_OFF')
        op.name = lr_tools.unhide_by_name
        op.hide = False
        row.prop(lr_tools, "unhide_by_name",icon_only=False)


        row = layout.column_flow(columns=2,align=True)

        op = row.operator("object.lr_hide_subd_modifier", text="SubD", icon = 'HIDE_ON')
        op.hide_subsurf = True
        op.hide_subsurf_active = False
        op = row.operator("object.lr_hide_subd_modifier", text="SubD", icon = 'HIDE_OFF')
        op.hide_subsurf = False
        op.hide_subsurf_active = False





        layout = self.layout.box()
        layout.label(text="Naming")

        layout.operator("object.lr_name_ucx", text="Name UCX_", icon = 'FILE_TEXT')        
        

        layout = self.layout.box()
        layout.label(text="Cleanup/Check")
        layout.operator("object.material_slot_remove_unused_on_selected",text="Remove unused Mat slots", icon='EXPORT')
        layout.operator("object.lr_material_cleanup",text="Material cleanup", icon='BRUSH_DATA')
        row = layout.row(align=True)
        row.operator("object.lr_assign_checker",text="Assign Checker", icon='TEXTURE')
        row.operator("object.lr_remove_checker",text="Remove Checker", icon='MESH_PLANE')




        # layout = self.layout.box()
        # layout.label(text="Export")
        # layout.operator("object.lr_export_but_one_material", text="With one material", icon='EXPORT')
        # layout.operator("object.lr_exportformask", text="With one material and one specified UVSet", icon='EXPORT')




class VIEW3D_PT_lr_mesh(bpy.types.Panel):
    bl_idname = "OBJECT_PT_lr_mesh"
    bl_label = "MESH"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "LR"

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    def draw(self, context):
        layout = self.layout.box()
        row = layout.row(align=True)
        row.operator("mesh.lr_get_edges_length", text="Get edges length", icon = 'MOD_LENGTH')


'''
class VIEW3D_PT_lr_uv(bpy.types.Panel):
    bl_idname = "OBJECT_PT_lr_uv"
    bl_label = "UV"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "LR"
    #	bl_context = "object"

    def draw(self, context):

        layout = self.layout.box()

        layout.label(text="UV Map selection")
        row = layout.row(align=True)
        lr_tools = context.scene.lr_tools

        set_index1 = row.operator("object.lr_uv_map_by_index", text="UV 1", icon = 'PASTEDOWN')
        set_index1.uv_index=1

        set_index2 = row.operator("object.lr_uv_map_by_index", text="UV 2", icon = 'PASTEDOWN')
        set_index2.uv_index=2

        set_index3 = row.operator("object.lr_uv_map_by_index", text="UV 3", icon = 'PASTEDOWN')
        set_index3.uv_index=3

        row = layout.row(align=True)
        row.operator("object.lr_uv_map_by_index_custom", text="Set UV index: ", icon = 'PASTEDOWN')
        row.scale_x = 0.3
        row.prop(lr_tools, "select_uv_index",icon_only=True)
        


        # layout.row().separator()
        row = layout.row(align=True)
        row.operator("object.lr_uv_index_name", text="Set UV name: ", icon = 'PASTEDOWN')
        #row.scale_x = 2
        row.prop(lr_tools, "name_to_uv_index_set",icon_only=True)

        layout.row().separator()

        layout = self.layout.box() 
        layout.label(text="UV Map control")

        row = layout.row(align=True)
        row.operator("object.mono_move_uv_map_up", text="Move Up", icon='TRIA_UP')
        row.operator("object.mono_move_uv_map_down", text="Move Down", icon = 'TRIA_DOWN')



        # layout.row().separator()

        
        row = layout.row(align=True)

        row.operator("object.lr_new_uv_set", text="New UV:", icon='PRESET_NEW')


        row.prop(lr_tools, "uv_map_new_name",icon_only=True)

        # layout.row().separator()





        row = layout.row(align=True)
        row.operator("object.lr_rename_active_uv_set", text="Rename:", icon ='FILE_TEXT')

        row.prop(lr_tools, "uv_map_rename",icon_only=True)

        # layout.row().separator()



        col = layout.column(align=True)
        c_row = col.row(align=True)
        c_row.operator("object.lr_remove_uv_by_name", text="Remove:", icon ='REMOVE')
        c_row.prop(lr_tools, "uv_map_delete_by_name",icon_only=True)
        
        col.operator("object.lr_remove_active_uv_set", text="Remove active", icon ='REMOVE')
        
        
        c_row = col.row(align=True)
        op = c_row.operator("object.lr_remove_uv_set_by_index", text="Remove UV index: ", icon = 'PASTEDOWN')
        op.uv_index = bpy.data.scenes['Scene'].lr_tools.remove_uv_index
        c_row.scale_x = 0.3
        c_row.prop(lr_tools, "remove_uv_index",icon_only=True)


class VIEW3D_PT_lr_uv(bpy.types.Panel):
    bl_label = "UV Control"
    bl_idname = "OBJECT_PT_lr_uv"
    bl_parent_id = "DATA_PT_uv_texture"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"
    bl_category = "LR"
    #	bl_context = "object"

    def draw(self, context):

        layout = self.layout.box() #UV Select

        layout.label(text="UV Select")
        row = layout.row(align=True)
        lr_tools = context.scene.lr_tools

        set_index1 = row.operator("object.lr_uv_map_by_index", text="UV 1", icon = 'PASTEDOWN')
        set_index1.uv_index=1

        set_index2 = row.operator("object.lr_uv_map_by_index", text="UV 2", icon = 'PASTEDOWN')
        set_index2.uv_index=2

        set_index3 = row.operator("object.lr_uv_map_by_index", text="UV 3", icon = 'PASTEDOWN')
        set_index3.uv_index=3

        row = layout.row(align=True)
        row.operator("object.lr_uv_map_by_index_custom", text="Set UV index: ", icon = 'PASTEDOWN')
        row.scale_x = 0.3
        row.prop(lr_tools, "select_uv_index",icon_only=True)
        
        row = layout.row(align=True)
        row.operator("object.lr_uv_index_name", text="Set UV name: ", icon = 'PASTEDOWN')
        row.prop(lr_tools, "name_to_uv_index_set",icon_only=True)

        layout.row().separator()


        layout = self.layout.box()  #UV Create
        layout.label(text="UV Add & Remove")

        row = layout.row(align=True)
        row.operator("object.lr_new_uv_set", text="New UV:", icon='PRESET_NEW')
        row.prop(lr_tools, "uv_map_new_name",icon_only=True)

        col = layout.column(align=True)
        c_row = col.row(align=True)
        c_row.operator("object.lr_remove_uv_by_name", text="Remove:", icon ='REMOVE')
        c_row.prop(lr_tools, "uv_map_delete_by_name",icon_only=True)
        col.operator("object.lr_remove_active_uv_set", text="Remove active", icon ='REMOVE')


        layout = self.layout.box() #UV Rename
        layout.label(text="UV Rename")
        
        row = layout.row(align=True)
        row.operator("object.lr_rename_active_uv_set", text="Rename:", icon ='FILE_TEXT')
        row.prop(lr_tools, "uv_map_rename",icon_only=True)

        layout = self.layout.box() #UV Move
        layout.label(text="UV Move")
        
        row = layout.row(align=True)
        row.operator("object.mono_move_uv_map_up", text="Move Up", icon='TRIA_UP')
        row.operator("object.mono_move_uv_map_down", text="Move Down", icon = 'TRIA_DOWN')
       
        c_row = col.row(align=True)
        op = c_row.operator("object.lr_remove_uv_set_by_index", text="Remove UV index: ", icon = 'PASTEDOWN')
        op.uv_index = bpy.data.scenes['Scene'].lr_tools.remove_uv_index
        c_row.scale_x = 0.3
        c_row.prop(lr_tools, "remove_uv_index",icon_only=True)
'''

class VIEW3D_PT_lr_select_uv(bpy.types.Panel):
    bl_label = "Select"
    bl_idname = "OBJECT_PT_lr_select_uv"
    bl_parent_id = "DATA_PT_uv_texture"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"
    bl_category = "LR"
    # bl_options = {'DEFAULT_CLOSED'}
    def draw(self, context):
        
        # layout = self.layout.box() #UV Select
        layout = self.layout
        lr_tools = context.scene.lr_tools
        # layout.label(text="UV Select")
        
        row = layout.row(align=True)
        row.scale_y = 1.5
        set_index1 = row.operator("object.lr_uv_map_by_index", text="UV 1", icon = 'PASTEDOWN')
        set_index1.uv_index=1
        

        set_index2 = row.operator("object.lr_uv_map_by_index", text="UV 2", icon = 'PASTEDOWN')
        set_index2.uv_index=2

        set_index3 = row.operator("object.lr_uv_map_by_index", text="UV 3", icon = 'PASTEDOWN')
        set_index3.uv_index=3

        
        row = layout.row(align=True)
        row.operator("object.lr_uv_map_by_index_custom", text="Set UV index: ", icon = 'PASTEDOWN')
        row.scale_x = 0.3
        row.prop(lr_tools, "select_uv_index",icon_only=True)
        
        
        row = layout.row(align=True)
        row.operator("object.lr_uv_index_name", text="Set UV Name: ", icon = 'PASTEDOWN')
        row.prop(lr_tools, "name_to_uv_index_set",icon_only=True)



class VIEW3D_PT_lr_move_uv(bpy.types.Panel):
    bl_label = "Move"
    bl_idname = "OBJECT_PT_lr_uv"
    bl_parent_id = "DATA_PT_uv_texture"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"
    bl_category = "LR"
    #	bl_context = "object"
    bl_options = {'DEFAULT_CLOSED'}
    def draw(self, context):
        
        layout = self.layout #UV Move
        lr_tools = context.scene.lr_tools
        # layout.label(text="UV Move")
        
        row = layout.row(align=True)
        row.operator("object.mono_move_uv_map_up", text="Move Up", icon='TRIA_UP')
        row.operator("object.mono_move_uv_map_down", text="Move Down", icon = 'TRIA_DOWN')
       
        col = layout.column(align=True)
        c_row = col.row(align=True)
        op = c_row.operator("object.lr_remove_uv_set_by_index", text="Remove UV index: ", icon = 'PASTEDOWN')
        op.uv_index = bpy.data.scenes['Scene'].lr_tools.remove_uv_index
        c_row.scale_x = 0.3
        c_row.prop(lr_tools, "remove_uv_index",icon_only=True)


class VIEW3D_PT_lr_rename_uv(bpy.types.Panel):
    bl_label = "Rename"
    bl_idname = "OBJECT_PT_lr_rename_uv"
    bl_parent_id = "DATA_PT_uv_texture"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"
    bl_category = "LR"
    #	bl_context = "object"
    bl_options = {'DEFAULT_CLOSED'}
    def draw(self, context):
        layout = self.layout #UV Move
        lr_tools = context.scene.lr_tools
        # layout.label(text="UV Rename")
        
        row = layout.row(align=True)
        row.operator("object.lr_rename_active_uv_set", text="Rename:", icon ='FILE_TEXT')
        row.prop(lr_tools, "uv_map_rename",icon_only=True)


class DATA_PT_lr_attribute_extend(bpy.types.Panel):

    bl_label = "Add & Remove"
    bl_idname = "OBJECT_PT_lr_attribute_menu_extend"
    bl_parent_id = "DATA_PT_mesh_attributes"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    # bl_context = "mesh"
    bl_category = "LR"
    # bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        lr_tools = context.scene.lr_tools
        layout = self.layout  #UV Create
        row = layout.row(align=True)
        row.operator("geometry.lr_add_attribute", text="New Attribute", icon='PRESET_NEW')
        row.operator("geometry.lr_remove_attribute", text="Remove by name", icon ='REMOVE')
        # Mark the operator properties as user-adjustable


class VIEW3D_PT_lr_add_remove_uv(bpy.types.Panel):
    bl_label = "Add & Remove"
    bl_idname = "OBJECT_PT_lr_add_remove_uv"
    bl_parent_id = "DATA_PT_uv_texture"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"
    bl_category = "LR"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout  #UV Create
        lr_tools = context.scene.lr_tools
        # layout.label(text="UV Add & Remove")

        row = layout.row(align=True)
        row.operator("object.lr_new_uv_set", text="New UV:", icon='PRESET_NEW')
        row.prop(lr_tools, "uv_map_new_name",icon_only=True)

        col = layout.column(align=True)
        col.operator("object.lr_remove_active_uv_set", text="Remove Active", icon ='REMOVE')
        c_row = col.row(align=True)
        c_row.operator("object.lr_remove_uv_by_name", text="Remove:", icon ='REMOVE')
        c_row.prop(lr_tools, "uv_map_delete_by_name",icon_only=True)
        
        



class OPN_OT_open_folder(Operator):
    """Opens Current Folder"""
    bl_idname = "window.open_path"
    bl_label = "Open Current .blend Path"
    bl_description = "Opens Current .blend Path"
    bl_space_type =  "Window"
    bl_region_type = "UI"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        full_path = bpy.path.abspath("//")
        subprocess.Popen('explorer "{0}"'.format(full_path))
        
        return {'FINISHED'}

def menu_func(self, context):
    self.layout.operator(OPN_OT_open_folder.bl_idname)
 

#UI End ---------------------------------------------------------------------------------
classes = (AddonPreferences,
            lr_tool_settings,
            # window_management.WINDOW_OT_lr_window_popup,
            # lr_exportformask,             #Moved to LR Export Addon
            # lr_export_but_one_material,   #Moved to LR Export Addon
            OPN_OT_open_folder,
            LR_Unwrap,
            OBJECT_OT_lr_assign_vertex_color,
            lr_offset_vertex_color,
            lr_vertex_rgb_to_alpha,
            lr_select_obj_by_topology,
            lr_replace_children,
            UCX.hideUCX,
            UCX.nameUCX,
            UCX.unhideUCX,
            UCX.hide_unhide_lattice,
            uv_misc.OBJECT_OT_lr_uv_map_by_index_custom,
            uv_misc.OBJECT_OT_lr_uv_map_by_index,
            uv_misc.UVIndexName,
            uv_misc.NewUVSet,
            uv_misc.RemoveActiveUVSet,
            uv_misc.RenameActiveUVSet,
            uv_misc.lr_replaceobjects,
            uv_misc.move_uv_map_up,
            uv_misc.move_uv_map_down,
            uv_misc.lr_remove_uv_by_name,
            uv_misc.OBJECT_OT_remove_uv_by_index,
            uv_misc.lr_randomize_uv_offset,
            uv_misc.lr_grid_redistribute_uv_islands,
            mesh_misc.OBJECT_OT_material_slot_remove_unused_on_selected,
            mesh_misc.MESH_OT_getEdgesLength,
            mesh_misc.OBJECT_OT_view_object_rotate,
            mesh_misc.OBJECT_OT_hide_by_name,
            mesh_misc.OBJECT_OT_hide_subsurf_modifier,
            mesh_misc.OBJECT_OT_hide_wire_objects,
            mesh_misc.OBJECT_OT_lr_assign_checker,
            mesh_misc.OBJECT_OT_lr_remove_checker,
            mesh_misc.OBJECT_OT_lr_material_cleanup,
            mesh_misc.OBJECT_OT_lr_set_collection_offset_from_empty,
            mesh_misc.OBJECT_OT_lr_rebuild,
            lr_pick_vertex_color,
            lr_multires_sculpt_offset,
            lr_deselect_duplicate,
            VIEW3D_PT_lr_vertex,
            VIEW3D_PT_lr_mesh,
            # VIEW3D_PT_lr_uv,
            
            DATA_PT_lr_attribute_extend,
            VIEW3D_PT_lr_select_uv,
            VIEW3D_PT_lr_move_uv,
            VIEW3D_PT_lr_rename_uv,
            VIEW3D_PT_lr_add_remove_uv,

            VIEW3D_PT_lr_object,
            OBJECT_OT_lr_drop_object,
            #VIEW3D_PT_lr_ucx

            #Attributes
            OBJECT_OT_lr_add_attribute, 
            OBJECT_OT_lr_remove_attribute

            )


@persistent
def lr_palette(scene):
    pal = bpy.data.palettes.get("LR_ID")
    if pal is None:
        pal = bpy.data.palettes.new("LR_ID")
        # add a color to that palette
        red = pal.colors.new()
        red.color = (1, 0, 0)
        red.weight = 1.0

        green = pal.colors.new()
        green.color = (0, 1, 0)
        green.weight = 1.0

        blue = pal.colors.new()
        blue.color = (0, 0, 1)
        blue.weight = 1.0

        cyan = pal.colors.new()
        cyan.color = (0, 1, 1)
        cyan.weight = 1.0

        saddlebrown = pal.colors.new()
        saddlebrown.color = (0.55, 0.27, 0.07)
        saddlebrown.weight = 1.0

        forestgreen = pal.colors.new()
        forestgreen.color = (0.13, 0.55, 0.13)
        forestgreen.weight = 1.0

        steelblue = pal.colors.new()
        steelblue.color = (0.27, 0.51, 0.71)
        steelblue.weight = 1.0

        indigo = pal.colors.new()
        indigo.color = (0.29, 0, 0.51)
        indigo.weight = 1.0

        laserlemon = pal.colors.new()
        laserlemon.color = (1, 1, 0.33)
        laserlemon.weight = 1.0

        deeppink = pal.colors.new()
        deeppink.color = (1, 0.08, 0.58)
        deeppink.weight = 1.0

        bisque = pal.colors.new()
        bisque.color = (1, 0.89, 0.77)
        bisque.weight = 1.0

        white = pal.colors.new()
        white.color = (1, 1, 1)
        white.weight = 1.0

        black = pal.colors.new()
        black.color = (0, 0, 0)
        black.weight = 1.0

        gray = pal.colors.new()
        gray.color = (0.5, 0.5, 0.5)
        gray.weight = 1.0

        #make red active
        pal.colors.active = red
    ts = bpy.context.tool_settings   
    ts.image_paint.palette = pal








def register():
    #needs handlers to get scene acess, othervise not working
    bpy.app.handlers.load_post.append(lr_palette)
    bpy.types.TOPBAR_MT_file.append(menu_func) #For opening filepath in explorer
    
    for cls in classes:
        bpy.utils.register_class(cls)
    # To acess properties: bpy.data.scenes['Scene'].lr_tools
    bpy.types.Scene.lr_tools = bpy.props.PointerProperty(type=lr_tool_settings)
    register_keymaps()

    

def unregister():
    bpy.app.handlers.load_post.remove(lr_palette)
    bpy.types.TOPBAR_MT_file.remove(menu_func) #For opening filepath in explorer
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.lr_tools
    unregister_keymaps()



if __name__ == "__main__":
    register()
    
    

#classes = (LR_Unwrap)
#register, unregister = bpy.utils.register_classes_factory(classes)

