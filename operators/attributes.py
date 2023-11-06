import bpy


class OBJECT_OT_lr_add_attribute(bpy.types.Operator):
    bl_idname = "geometry.lr_add_attribute"
    bl_label = "Adds attribute on selected objects"
    bl_options = {'REGISTER', 'UNDO'}


    name: bpy.props.StringProperty(
        name="Name",
        description="Enter a string",
        default="Attribute",
    )

    domain: bpy.props.EnumProperty(
        name="Domain",
        description="Select a domain",
        items=[
            ('POINT', "Vertex", "Add attribute to vertex"),
            ('EDGE', "Edge", "Add attribute to edge"),
            ('FACE', "Face", "Add attribute to face"),
            ('CORNER', "Face Corner", "Add attribute to face corner"),
        ],
        default='POINT',
    )

    data_type: bpy.props.EnumProperty(
        name="Data Type",
        description="Select a data type",
        items=[
            ('FLOAT', "Float", "Float data type"),
            ('INT', "Integer", "Integer data type"),
            ('FLOAT_VECTOR', "Vector", "Vector data type"),
            ('FLOAT_COLOR', "Color", "Color data type"),
            ('BYTE_COLOR', "Byte Color", "Byte Color data type"),
            ('STRING', "String", "String data type"),
            ('BOOLEAN', "Boolean", "Boolean data type"),
            ('FLOAT_2', "2D Vector", "2D Vector data type"),
            ('INT8', "8-Bit Integer", "8-Bit Integer data type"),
            ('INT32_2D', "2D Integer Vector", "2D Integer Vector data type"),
            ('QUATERNION', "Quaternion", "Quaternion data type"),
        ],
        default='FLOAT',
    )

    @classmethod
    def poll(cls, context): 
        return context.mode == 'OBJECT' or context.mode == 'EDIT_MESH'
        
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        for obj in bpy.context.selected_objects:
            if obj.type == 'MESH' or obj.type == 'CURVE' or obj.type == 'EMPTY':

                if obj.data.attributes.get(self.name) == None: #Check if attribute is already present.
                    obj.data.attributes.new(name=self.name,
                                            type=self.data_type,
                                            domain=self.domain)
        

        # self.report({'INFO'}, f'Updated {num} objects.')
        return {'FINISHED'}		




class OBJECT_OT_lr_remove_attribute(bpy.types.Operator):
    bl_idname = "geometry.lr_remove_attribute"
    bl_label = "Removes attribute on selected objects"
    bl_options = {'REGISTER', 'UNDO'}


    name: bpy.props.StringProperty(
        name="Name",
        description="Enter a string",
        default="Attribute",
    )


    @classmethod
    def poll(cls, context): 
        return context.mode == 'OBJECT' or context.mode == 'EDIT_MESH'
        
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):

        for obj in bpy.context.selected_objects:
            if obj.type == 'MESH' or obj.type == 'CURVE' or obj.type == 'EMPTY':

                if obj.data.attributes.get(self.name): #Check if attribute is already present.
                    obj.data.attributes.remove(obj.data.attributes[self.name])
                else:
                    message= f'Property: {self.name} not present on object: {obj.name}'
                    self.report({'INFO'}, message)


        return {'FINISHED'}		

