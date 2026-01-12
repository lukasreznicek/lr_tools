import bpy

class SCENE_OT_lr_set_scene_scale_to_meters(bpy.types.Operator):
    """Set scene units to meters (scale=0.01) and adjust 3D view clipping"""
    bl_idname = "scene.lr_set_unit_to_meters"
    bl_label = "Scene Scale Presets"
    bl_options = {'REGISTER', 'UNDO'}

    unit_scale: bpy.props.EnumProperty(
        name="Unit Scale",
        description="Choose the unit scale for the scene",
        items=[
            ('METERS', "Meters", "Set scene scale to meters (0.01)"),
            ('CENTIMETERS', "Centimeters", "Set scene scale to centimeters (0.001)")
        ],
        default='METERS'
    )
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
    # @classmethod
    # def poll(cls, context):
    #     # Only visible in 3D View
    #     return context.space_data is None or context.space_data.type in {'VIEW_3D'}
    # def draw(self, context):
    #     layout = self.layout
    #     layout.prop(self, "unit_scale")


    def execute(self, context):
        # Set scene unit scale
        # bpy.data.screens["Layout"].areas[3].spaces[0].clip_end = 89
        # bpy.data.screens["Layout"].areas[3].spaces[0].clip_start = 777

        # for area in context.window.screen.areas:
        #     if area.type == 'VIEW_3D':
        #         for space in area.spaces:
        #             if space.type == 'VIEW_3D':
        #                 print("found")
        #                 print(space.type)
        #                 print(space.clip_start)
        #                 space.clip_start = 666
        if self.unit_scale == "METERS":
            context.scene.unit_settings.scale_length = 0.01
            
            # Set 3D view clipping distances
            # for area in context.window.screen.areas:
            #     if area.type == 'VIEW_3D':
            #         for space in area.spaces:
            #             if space.type == 'VIEW_3D':
            #                 space.clip_start = 100
            #                 space.clip_end = 100000
                            
            self.report({'INFO'}, "Scene scale set to 0.01 (meters)")

        if self.unit_scale == "CENTIMETERS":
            
            context.scene.unit_settings.scale_length = 1
            #comment is done by hatch
            # # Set 3D view clipping distances
            # for area in context.window.screen.areas:
            #     if area.type == 'VIEW_3D':
            #         for space in area.spaces:
            #             print("Im")
            #             if space.type == 'VIEW_3D':
            #                 space.clip_start = 0.01
            #                 space.clip_end = 1000
            self.report({'INFO'}, "Scene scale set to 1 (centimeters)")


        return {'FINISHED'}
