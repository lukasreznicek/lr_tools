
import bpy
class lr_name_high_poly_bake(bpy.types.Operator):
    """Name inactive object(s) based on active object's name, replacing low poly suffix with high poly suffix, works for substance painter bake name matching . Including suffixes after '_low' \n\nIf Active object is missing _lp suffix, it will be added. \nIf multiple inactive objects(high poly) are selected, they will be numbered"""
    bl_idname = "lr.name_high_poly_bake"
    bl_label = "Copy Active Name to Inactive"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        #check if active object is mesh
        if context.mode != 'OBJECT':
            self.report({'WARNING'}, "Object mode is required.")
            return {'CANCELLED'}
        

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
                inactive_objs[0].name = active_obj.name + "_hp"
                active_obj.name = active_obj.name + "_lp"
            else:
                for idx, obj in enumerate(inactive_objs):
                    obj.name=inactive_objs[idx].name = active_obj.name+f"_hp_{idx:02d}"
                active_obj.name = active_obj.name + "_lp"

        return {'FINISHED'}




