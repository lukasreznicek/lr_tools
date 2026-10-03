from . import attributes, material, mesh, naming, object, paint, scene, sculpt, uv, vertex_color, view3d, window

classes = (
    # Vertex color
    vertex_color.OBJECT_OT_lr_assign_vertex_color,
    vertex_color.lr_offset_vertex_color,
    vertex_color.lr_pick_vertex_color,
    vertex_color.lr_vertex_rgb_to_alpha,

    # UV
    uv.OBJECT_OT_lr_uv_map_by_index_custom,
    uv.OBJECT_OT_lr_uv_map_by_index,
    uv.UVIndexName,
    uv.NewUVSet,
    uv.RemoveActiveUVSet,
    uv.RenameActiveUVSet,
    uv.lr_replaceobjects,
    uv.move_uv_map_up,
    uv.move_uv_map_down,
    uv.lr_remove_uv_by_name,
    uv.OBJECT_OT_remove_uv_by_index,
    uv.lr_randomize_uv_offset,
    uv.lr_grid_redistribute_uv_islands,
    uv.LR_Tools_OT_UVCopyPaste,
    uv.LR_TOOLS_OT_uv_offset_by_object_id,
    uv.UV_OT_scale_from_corner,
    uv.UV_OT_snap_to_corner,

    # Attributes
    attributes.OBJECT_OT_lr_add_attribute,
    attributes.OBJECT_OT_lr_attribute_increment_values_mesh,
    attributes.OBJECT_OT_lr_remove_attribute,
    attributes.OBJECT_OT_lr_obj_info_id_by_uv_island,
    attributes.OBJECT_OT_lr_attribute_select_by_index,
    attributes.OBJECT_OT_lr_attribute_select_by_name,
    attributes.OBJECT_OT_lr_set_obj_info_attr,
    attributes.OBJECT_OT_lr_recover_obj_info,
    attributes.OBJECT_OT_lr_attribute_increment_int_values,

    # Material
    material.OBJECT_OT_material_slot_remove_unused_on_selected,
    material.OBJECT_OT_lr_material_cleanup,
    material.OBJECT_OT_lr_assign_checker,
    material.OBJECT_OT_lr_remove_checker,

    # Naming / UCX
    naming.lr_name_high_poly_bake,
    naming.hideUCX,
    naming.OBJECT_OT_selectObjectCollisions,
    naming.OBJECT_OT_NameUCX,
    naming.unhideUCX,
    naming.hide_unhide_lattice,

    # Object
    object.OBJECT_OT_lr_origin_to_selection,
    object.OBJECT_OT_lr_MeshCut,
    object.OBJECT_OT_lr_select_children_on_selected_objects,
    object.OBJECT_OT_lr_select_root_parent,
    object.OBJECT_OT_select_bevel_object,
    object.OBJECT_OT_lr_drop_object,
    object.lr_replace_children,
    object.lr_select_obj_by_topology,
    object.lr_deselect_duplicate,
    object.OBJECT_OT_delete_modifier,
    object.OBJECT_OT_SwitchShapeKeyOnMultipleObjects,
    object.OBJECT_OT_hide_by_name,
    object.OBJECT_OT_hide_subsurf_modifier,
    object.OBJECT_OT_hide_wire_objects,
    object.OBJECT_OT_lr_set_collection_offset_from_empty,
    object.OBJECT_OT_lr_rebuild,
    object.OBJECT_OT_join_selection_and_parent_bmesh,

    # Mesh
    mesh.MESH_OT_lr_sculpt_selected,
    mesh.MESH_OT_getEdgesLength,

    # Sculpt
    sculpt.lr_multires_sculpt_offset,

    # Paint
    paint.PAINT_OT_lr_screen_color_picker,

    # View3D
    view3d.VIEW3D_OT_snap_cursor_to_active,
    view3d.LR_OT_view_object_rotate,

    # Scene / Window
    scene.SCENE_OT_lr_set_scene_scale_to_meters,
    window.WM_OT_ToggleTabletAPI,
    window.OPN_OT_open_folder,
    window.OPN_OT_open_config,
)
