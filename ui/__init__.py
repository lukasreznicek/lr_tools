from . import menus, panels, pie_menus

classes = (
    panels.DATA_PT_lr_attribute_extend,
    panels.VIEW3D_PT_lr_vertex,
    panels.VIEW3D_PT_lr_mesh,
    panels.VIEW3D_PT_lr_select_uv,
    panels.VIEW3D_PT_lr_move_uv,
    panels.VIEW3D_PT_lr_rename_uv,
    panels.VIEW3D_PT_lr_add_remove_uv,
    panels.UI_PT_Panel_UV_Editor,
    panels.VIEW3D_PT_lr_object,
    panels.VIEW3D_PT_lr_origin_info,
    panels.VIEW3D_PT_lr_delete_modifier,

    menus.VIEW3D_MT_LR_Menu,

    pie_menus.VIEW3D_MT_Shading_Ex,
    pie_menus.WM_OT_NewEditorWindow,
    pie_menus.VIEW3D_MT_WindowsPopUp,
    pie_menus.VIEW3D_MT_LRPieSave,
    pie_menus.VIEW3D_MT_Select_Ops_Pie,
    pie_menus.VIEW3D_MT_3DCursor,
)
