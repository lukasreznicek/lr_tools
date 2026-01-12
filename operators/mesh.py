import bpy, bmesh
from mathutils import Matrix, Vector

class MESH_OT_lr_sculpt_selected(bpy.types.Operator):
    """Sculpt Selected"""
    bl_idname = "mesh.lr_sculpt_selected"
    bl_label = "Sculpt Selected"
    bl_options = {'REGISTER', 'UNDO'}  # enables Undo and display in the operator panel

    def execute(self, context):
        # Your main logic goes here
        active_object = context.active_object
        sel_mode = context.tool_settings.mesh_select_mode

        if context.mode == 'EDIT_MESH':
            if sel_mode[2]: #Faces
                # bm = bmesh.from_edit_mesh(active_object.data)
                # store_face_sel = [f.index for f in bm.faces if f.select]
                
                #bpy.ops.mesh.select_more()
                bpy.ops.mesh.reveal(select=False)
                bpy.ops.mesh.hide(unselected=False)
                bpy.ops.object.mode_set(mode='SCULPT')

                bpy.ops.paint.mask_flood_fill(mode='VALUE', value=0)
                bpy.ops.paint.visibility_invert()
                bpy.ops.paint.mask_flood_fill(mode='VALUE', value=1)

                bpy.ops.paint.hide_show_all(action='SHOW')
                bpy.ops.paint.mask_flood_fill(mode='INVERT')

            if sel_mode[0] or sel_mode[1]: #Verts                
                if sel_mode[1]:
                    sel_mode[0] = True
                    sel_mode[1] = False
                
                bpy.ops.mesh.reveal(select=False)
                bpy.ops.mesh.hide(unselected=False)
                bpy.ops.object.mode_set(mode='SCULPT')
                bpy.ops.paint.visibility_invert()
                bpy.ops.paint.mask_flood_fill(mode='VALUE', value=0)
                bpy.ops.paint.visibility_invert()
                bpy.ops.paint.mask_flood_fill(mode='VALUE', value=1)
                bpy.ops.paint.hide_show_all(action='SHOW')

                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.mode_set(mode='SCULPT')

        self.report({'INFO'}, "Done")
        return {'FINISHED'}
    
'''

def get_right_and_up_axes(context, mx):
    r3d = context.space_data.region_3d

    view_right = r3d.view_rotation @ Vector((1, 0, 0))
    view_up = r3d.view_rotation @ Vector((0, 1, 0))

    axes_right = []
    axes_up = []

    for idx, axis in enumerate([Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))]):
        dot = view_right.dot(mx.to_3x3() @ axis)
        axes_right.append((dot, idx))
        dot = view_up.dot(mx.to_3x3() @ axis)
        axes_up.append((dot, idx))

    axis_right = max(axes_right, key=lambda x: abs(x[0]))
    axis_up = max(axes_up, key=lambda x: abs(x[0]))
    flip_right = True if axis_right[0] < 0 else False
    flip_up = True if axis_up[0] < 0 else False
    return axis_right[1], axis_up[1], flip_right, flip_up


def get_selected_vert_sequences(verts, ensure_seq_len=False, debug=False):
    sequences = []
    noncyclicstartverts = [v for v in verts if len([e for e in v.link_edges if e.select]) == 1]

    if noncyclicstartverts:
        v = noncyclicstartverts[0]

    else:
        v = verts[0]

    seq = []

    while verts:
        seq.append(v)

        if v not in verts:
            break

        else:
            verts.remove(v)

        if v in noncyclicstartverts:
            noncyclicstartverts.remove(v)

        nextv = [e.other_vert(v) for e in v.link_edges if e.select and e.other_vert(v) not in seq]

        if nextv:
            v = nextv[0]

        else:
            cyclic = True if len([e for e in v.link_edges if e.select]) == 2 else False

            sequences.append((seq, cyclic))

            if verts:
                if noncyclicstartverts:
                    v = noncyclicstartverts[0]
                else:
                    v = verts[0]

                seq = []

    if ensure_seq_len:
        seqs = []

        for seq, cyclic in sequences:
            if len(seq) > 1:
                seqs.append((seq, cyclic))

        sequences = seqs

    if debug:
        for seq, cyclic in sequences:
            print(cyclic, [v.index for v in seq])

    return sequences

def get_selection_islands(faces, debug=False):
    if debug:
        print("selected:", [f.index for f in faces])

    face_islands = []

    while faces:
        island = [faces[0]]
        foundmore = [faces[0]]

        if debug:
            print("island:", [f.index for f in island])
            print("foundmore:", [f.index for f in foundmore])

        while foundmore:
            for e in foundmore[0].edges:
                bf = [f for f in e.link_faces if f.select and f not in island]
                if bf:
                    island.append(bf[0])
                    foundmore.append(bf[0])

            if debug:
                print("popping", foundmore[0].index)

            foundmore.pop(0)

        face_islands.append(island)

        for f in island:
            faces.remove(f)

    if debug:
        print()
        for idx, island in enumerate(face_islands):
            print("island:", idx)
            print(" » ", ", ".join([str(f.index) for f in island]))

    islands = []

    for fi in face_islands:
        vi = set()
        ei = set()

        for f in fi:
            vi.update(f.verts)
            ei.update(f.edges)

        islands.append((list(vi), list(ei), fi))

    return sorted(islands, key=lambda x: len(x[2]), reverse=True)

def popup_message(message, title="Info", icon="INFO", terminal=True):
    def draw_message(self, context):
        if isinstance(message, list):
            for m in message:
                self.layout.label(text=m)
        else:
            self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw_message, title=title, icon=icon)

    if terminal:
        if icon == "FILE_TICK":
            icon = "ENABLE"
        elif icon == "CANCEL":
            icon = "DISABLE"
        print(icon, title)

        if isinstance(message, list):
            print(" »", ", ".join(message))
        else:
            print(" »", message)
#From machine tools

class MESH_OT_AlignEditMesh(bpy.types.Operator):
    bl_idname = "mesh.lr_align_editmesh"
    bl_label = "LR: Align (Edit Mesh)"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Local Space Align\nALT: World Space Align\nCTRL: Cursor Space Align"

    mode: bpy.props.EnumProperty(name="Mode", items=align_mode_items, default="VIEW")
    type: bpy.props.EnumProperty(name="Type", items=align_type_items, description="Align to Min or Max, Average, Zero or Cursor", default="MIN")
    axis: bpy.props.EnumProperty(name="Axis", items=axis_items, description="Align on the X, Y or Z Axis", default="X")
    direction: bpy.props.EnumProperty(name="Direction", items=align_direction_items, default="LEFT")
    space: bpy.props.EnumProperty(name="Space", items=align_space_items, description="Align in Local, World or Cursor Space", default="LOCAL")
    align_each: bpy.props.BoolProperty(name="Align Each Island independently", default=False)
    draw_each: bpy.props.BoolProperty()

    @classmethod
    def poll(cls, context):
        if context.mode == "EDIT_MESH":
            active = context.active_object
            bm = bmesh.from_edit_mesh(active.data)
            return [v for v in bm.verts if v.select]

    def draw(self, context):
        
        layout = self.layout
        column = layout.column(align=True)

        split = column.split(factor=0.15, align=True)
        split.label(text='Space')
        row = split.row(align=True)
        row.prop(self, 'space', expand=True)

        split = column.split(factor=0.15, align=True)
        split.label(text='Axis')
        row = split.row(align=True)
        row.prop(self, 'axis', expand=True)

        split = column.split(factor=0.15, align=True)
        split.label(text='Type')
        row = split.row(align=True)
        row.prop(self, 'type', expand=True)

        if self.draw_each:
            split = column.split(factor=0.15, align=True)
            split.label(text='Each')
            row = split.row(align=True)
            row.prop(self, 'align_each', text='True' if self.align_each else 'False', toggle=True)

    def invoke(self, context, event):
        self.space = 'WORLD' if event.alt else 'CURSOR' if event.ctrl else 'LOCAL'

        if self.mode == 'VIEW':
            axis_right, axis_up, flip_right, flip_up = get_right_and_up_axes(context, mx=self.get_matrix(context))

            if self.type in ['ZERO', 'AVERAGE', 'CURSOR'] and self.direction in ['HORIZONTAL', 'VERTICAL']:
                axis = axis_right if self.direction == "HORIZONTAL" else axis_up

            elif self.direction in ['LEFT', 'RIGHT', 'TOP', 'BOTTOM']:
                axis = axis_right if self.direction in ['RIGHT', 'LEFT'] else axis_up

                if self.direction == 'RIGHT':
                    self.type = 'MIN' if flip_right else 'MAX'

                elif self.direction == 'LEFT':
                    self.type = 'MAX' if flip_right else 'MIN'

                elif self.direction == 'TOP':
                    self.type = 'MIN' if flip_up else 'MAX'

                elif self.direction == 'BOTTOM':
                    self.type = 'MAX' if flip_up else 'MIN'

            else:
                popup_message(f"You can't combine {self.type} with {self.direction}!", title="Invalid Property Combination")
                return {'CANCELLED'}

            self.axis = 'X' if axis == 0 else 'Y' if axis == 1 else 'Z'

        return self.execute(context)

    def execute(self, context):
        axis_index_mapping = {'X': 0,
                      'Y': 1,
                      'Z': 2}
        self.align(context, self.type, axis_index_mapping[self.axis], self.space)
        return {'FINISHED'}

    def align(self, context, type, axis, space):
        active = context.active_object
        mx = self.get_matrix(context)

        bm = bmesh.from_edit_mesh(active.data)
        bm.normal_update()
        bm.verts.ensure_lookup_table()

        all_verts = []
        verts = [v for v in bm.verts if v.select]

        if tuple(bpy.context.scene.tool_settings.mesh_select_mode) == (True, False, False) or type in ['ZERO', 'CURSOR']:
            all_verts.append(verts)
            self.draw_each = False

        elif tuple(bpy.context.scene.tool_settings.mesh_select_mode) == (False, True, False):
            sequences = get_selected_vert_sequences(verts.copy(), debug=False)
            eachable = len(sequences) > 1

            if eachable:
                self.draw_each = True

            if eachable and self.align_each:
                for verts, _ in sequences:
                    all_verts.append(verts)

            else:
                all_verts.append(verts)

        elif tuple(bpy.context.scene.tool_settings.mesh_select_mode) == (False, False, True):
            islands = get_selection_islands([f for f in bm.faces if f.select], debug=False)
            eachable = len(islands) > 1

            if eachable:
                self.draw_each = True

            if eachable and self.align_each:
                for verts, _, _ in islands:
                    all_verts.append(verts)
            else:
                all_verts.append(verts)

        for verts in all_verts:

            if space == 'LOCAL':
                axiscoords = [v.co[axis] for v in verts]

            elif space == 'WORLD':
                axiscoords = [(active.matrix_world @ v.co)[axis] for v in verts]

            elif space == 'CURSOR':
                axiscoords = [(mx.inverted_safe() @ active.matrix_world @ v.co)[axis] for v in verts]

            if self.type == "MIN":
                target = min(axiscoords)

            elif self.type == "MAX":
                target = max(axiscoords)

            elif self.type == "ZERO":
                target = 0

            elif self.type == "AVERAGE":
                target = sum(axiscoords) / len(axiscoords)

            elif type == "CURSOR":
                if space == 'LOCAL':
                    c_world = context.scene.cursor.location
                    c_local = mx.inverted_safe() @ c_world
                    target = c_local[axis]

                elif space == 'WORLD':
                    target = context.scene.cursor.location[axis]

                elif space == 'CURSOR':
                    target = 0

            for v in verts:
                if space == 'LOCAL':
                    v.co[axis] = target

                elif space == 'WORLD':
                    world_co = active.matrix_world @ v.co

                    world_co[axis] = target

                    v.co = active.matrix_world.inverted_safe() @ world_co

                elif space == 'CURSOR':
                    cursor_co = mx.inverted_safe() @ active.matrix_world @ v.co

                    cursor_co[axis] = target

                    v.co = active.matrix_world.inverted_safe() @ mx @ cursor_co

        bm.normal_update()
        bmesh.update_edit_mesh(active.data)

    def get_matrix(self, context):
        mx = context.active_object.matrix_world if self.space == 'LOCAL' else context.scene.cursor.matrix if self.space == 'CURSOR' else Matrix()
        return mx
'''