# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####


import bpy, bmesh, timeit
from mathutils import Vector
import numpy as np
from math import sqrt, radians
import random

'''
class WASPMED_OT_smooth_weight(bpy.types.Operator):
    #bl_idname = "object.WASPMED_OT_smooth_weight"
    bl_label = "Smooth Weight"
    bl_description = ("")
    bl_options = {'REGISTER', 'UNDO'}

    factor : bpy.props.FloatProperty(
        name="Factor", default=0.5, min=0, max=1)
    repeat : bpy.props.IntProperty(
        name="Max Thickness", default=1, min=0, soft_max=20,
        description="Thickness in the red area")
    expand : bpy.props.FloatProperty(
        name="Expand/Contract", default=0, min=-1, max=1)

    @classmethod
    def poll(cls, context):
        return len(context.object.vertex_groups) > 0

    def execute(self, context):
        context.object.data.use_paint_mask_vertex = True
        bpy.ops.paint.vert_select_all(action='SELECT')
        bpy.ops.object.vertex_group_smooth(factor=self.factor, repeat=self.repeat, expand=self.expand)
        context.object.data.use_paint_mask_vertex = False
        return {'FINISHED'}
'''

class OBJECT_OT_wm_weight_thickness(bpy.types.Operator):
    bl_idname = "object.wm_weight_thickness"
    bl_label = "Weight Thickness"
    bl_description = ("")
    bl_options = {'REGISTER', 'UNDO'}

    min_thickness : bpy.props.FloatProperty(
        name="Min Thickness", default=3, min=0.01, soft_max=10,
        description="Thickness in the blue area")
    max_thickness : bpy.props.FloatProperty(
        name="Max Thickness", default=6, min=0.01, soft_max=10,
        description="Thickness in the red area")

    @classmethod
    def poll(cls, context):
        return len(context.object.vertex_groups) > 0

    def execute(self, context):
        bool_flip = True
        min_iso, max_iso = 0.25, 0.75
        start_time = timeit.default_timer()
        try:
            check = bpy.context.object.vertex_groups[0]
        except:
            self.report({'ERROR'}, "The object doesn't have Vertex Groups")
            return {'CANCELLED'}

        ob0 = bpy.context.object

        group_id = ob0.vertex_groups.active_index
        vertex_group_name = ob0.vertex_groups[group_id].name

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.object.mode_set(mode='OBJECT')

        me0 = ob0.data

        # generate new bmesh
        bm = bmesh.new()
        bm.from_mesh(me0)
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        bm.faces.ensure_lookup_table()

        # store weight values
        weight = []
        ob = bpy.data.objects.new("temp", me0)
        for g in ob0.vertex_groups:
            ob.vertex_groups.new(name=g.name)
        for v in me0.vertices:
            try:
                weight.append(ob.vertex_groups[vertex_group_name].weight(v.index))
            except:
                weight.append(0)

        # define iso values
        iso_values = []
        n_cuts = 24
        for i_cut in range(n_cuts):
            delta_iso = abs(max_iso - min_iso)
            min_iso = min(min_iso, max_iso)
            if delta_iso == 0: iso_val = min_iso
            else: iso_val = i_cut*delta_iso/(n_cuts-1) + min_iso
            iso_values.append(iso_val)

        # Start Cuts Iterations
        filtered_edges = bm.edges
        for iso_val in iso_values:
            delete_edges = []

            faces_mask = []
            for f in bm.faces:
                w_min = 2
                w_max = 2
                for v in f.verts:
                    w = weight[v.index]
                    if w_min == 2:
                        w_max = w_min = w
                    if w > w_max: w_max = w
                    if w < w_min: w_min = w
                    if w_min < iso_val and w_max > iso_val:
                        faces_mask.append(f)
                        break
            #print("selected faces:" + str(len(faces_mask)))

            #link_faces = [[f for f in e.link_faces] for e in bm.edges]

            #faces_todo = [f.select for f in bm.faces]
            #faces_todo = [True for f in bm.faces]
            verts = []
            edges = []
            edges_id = {}
            _filtered_edges = []
            n_verts = len(bm.verts)
            count = n_verts
            for e in filtered_edges:
                #id0 = e.vertices[0]
                #id1 = e.vertices[1]
                id0 = e.verts[0].index
                id1 = e.verts[1].index
                w0 = weight[id0]
                w1 = weight[id1]

                if w0 == w1: continue
                elif w0 > iso_val and w1 > iso_val:
                    _filtered_edges.append(e)
                    continue
                elif w0 < iso_val and w1 < iso_val: continue
                elif w0 == iso_val or w1 == iso_val: continue
                else:
                    v0 = bm.verts[id0].co
                    v1 = bm.verts[id1].co
                    v = v0.lerp(v1, (iso_val-w0)/(w1-w0))
                    if e not in delete_edges:
                        delete_edges.append(e)
                    verts.append(v)
                    edges_id[str(id0)+"_"+str(id1)] = count
                    edges_id[str(id1)+"_"+str(id0)] = count
                    count += 1
                    _filtered_edges.append(e)
            filtered_edges = _filtered_edges
            #print("creating faces")
            splitted_faces = []

            switch = False
            # splitting faces
            for f in faces_mask:
                # create sub-faces slots. Once a new vertex is reached it will
                # change slot, storing the next vertices for a new face.
                build_faces = [[],[]]
                #switch = False
                verts0 = [v.index for v in f.verts]
                verts1 = list(verts0)
                verts1.append(verts1.pop(0)) # shift list
                for id0, id1 in zip(verts0, verts1):

                    # add first vertex to active slot
                    build_faces[switch].append(id0)

                    # try to split edge
                    try:
                        # check if the edge must be splitted
                        new_vert = edges_id[str(id0)+"_"+str(id1)]
                        # add new vertex
                        build_faces[switch].append(new_vert)
                        # if there is an open face on the other slot
                        if len(build_faces[not switch]) > 0:
                            # store actual face
                            splitted_faces.append(build_faces[switch])
                            # reset actual faces and switch
                            build_faces[switch] = []
                            # change face slot
                        switch = not switch
                        # continue previous face
                        build_faces[switch].append(new_vert)
                    except: pass
                if len(build_faces[not switch]) == 2:
                    build_faces[not switch].append(id0)
                if len(build_faces[not switch]) > 2:
                    splitted_faces.append(build_faces[not switch])
                # add last face
                splitted_faces.append(build_faces[switch])
                #del_faces.append(f.index)

            #print("generate new bmesh")
            # adding new vertices
            new_verts = []
            for v in verts:
                new_verts.append(bm.verts.new(v))
            #verts = [0]*len(verts) + verts
            bm.verts.index_update()
            bm.verts.ensure_lookup_table()
            # adding new faces
            missed_faces = []
            added_faces = []
            for f in splitted_faces:
                try:
                    face_verts = [bm.verts[i] for i in f]
                    new_face = bm.faces.new(face_verts)
                    for e in new_face.edges:
                        filtered_edges.append(e)
                except:
                    missed_faces.append(f)

            #print("missed " + str(len(missed_faces)) + " faces")
            bm.faces.ensure_lookup_table()
            # updating weight values
            weight = weight + [iso_val]*len(verts)

            # deleting old edges/faces
            bm.edges.ensure_lookup_table()
            for e in delete_edges:
                bm.edges.remove(e)
            _filtered_edges = []
            for e in filtered_edges:
                if e not in delete_edges: _filtered_edges.append(e)
            filtered_edges = _filtered_edges

        #print("creating curve")
        name = ob0.name + '_Contour'
        me = bpy.data.meshes.new(name)
        bm.to_mesh(me)
        ob = bpy.data.objects.new(name, me)

        # Link object to scene and make active
        bpy.context.collection.objects.link(ob)
        bpy.context.view_layer.objects.active = ob
        ob.select_set(True)
        ob0.select_set(False)

        # generate new vertex group
        for g in ob0.vertex_groups:
            ob.vertex_groups.new(name=g.name)
            ob.vertex_groups.new(name="Smooth")
        #ob.vertex_groups.new(name=vertex_group_name)

        #print("doing weight")
        all_weight = weight + [iso_val]*len(verts)
        #mult = 1/(1-iso_val)
        for id in range(len(all_weight)):
            #if False: w = (all_weight[id]-iso_val)*mult
            w = all_weight[id]
            direction = bool_flip
            for i in range(len(iso_values)-1):
                val0, val1 = iso_values[0], iso_values[-1]
                #val0, val1 = iso_values[i], iso_values[i+1]
                if val0 < w <= val1:
                    if direction: w1 = (w-val0)/(val1-val0)
                    else: w1 = (val1-w)/(val1-val0)
                direction = not direction
            if w < iso_values[0]: w1 = not bool_flip
            if w > iso_values[-1]: w1 = not direction
            w2 = w1
            if w == iso_values[0]: w2 = 1
            ob.vertex_groups[vertex_group_name].add([id], w1, 'REPLACE')
            #ob.vertex_groups["Smooth"].add([id], w2, 'REPLACE')
            #ob.vertex_groups["Smooth"].add([id], w>min_iso, 'REPLACE')
        #print("weight done")
        #for id in range(len(weight), len(ob.data.vertices)):
        #    ob.vertex_groups[vertex_group_name].add([id], iso_val*0, 'ADD')


        ob.vertex_groups.active_index = group_id

        # materials
        bpy.ops.object.material_slot_add()
        bpy.ops.object.material_slot_add()
        bpy.ops.object.material_slot_add()
        try: body_mat = bpy.data.materials["Body"]
        except: body_mat = bpy.data.materials.new("Body")
        try: border_mat = bpy.data.materials["Border"]
        except: border_mat = bpy.data.materials.new("Border")
        try: corset_mat = bpy.data.materials["Corset"]
        except: corset_mat = bpy.data.materials.new("Corset")
        corset_mat.diffuse_color = (0.31,0.737,0.792,1)
        border_mat.diffuse_color = (0.31*0.6, 0.737*0.6, 0.792*0.6,1)
        ob.material_slots[0].material = body_mat
        ob.material_slots[1].material = border_mat
        ob.material_slots[2].material = corset_mat
        for p in ob.data.polygons:
            bool_corset = True
            bool_body = True
            for v in p.vertices:
                #w = ob.vertex_groups["Group"].weight(v)
                w = ob.vertex_groups.active.weight(v)
                if w < 1: bool_corset = False
                if w > 0: bool_body = False
            if bool_corset: p.material_index = 2
            elif not bool_body: p.material_index = 1
            if not bool_body:
                for id in p.vertices:
                    ob.vertex_groups["Smooth"].add([id], 1, 'REPLACE')

        # align new object
        ob.matrix_world = ob0.matrix_world

        # Displace Modifier
        ob.modifiers.new(type='VERTEX_WEIGHT_EDIT', name='Profile')
        group_name = ob.vertex_groups.active.name
        bpy.context.object.modifiers["Profile"].vertex_group = group_name
        ob.modifiers.new(type='SOLIDIFY', name='Solidify')
        mod = ob.modifiers["Solidify"]
        mod.thickness = self.max_thickness
        mod.vertex_group = vertex_group_name
        mod.thickness_vertex_group = self.min_thickness / self.max_thickness
        mod.offset = 1

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_linked(delimit=set())
        bpy.ops.mesh.select_all(action='INVERT')
        bpy.ops.mesh.delete(type='VERT')
        bpy.ops.object.mode_set(mode='OBJECT')


        #bpy.ops.paint.weight_paint_toggle()
        #bpy.context.space_data.viewport_shade = 'WIREFRAME'
        ob.data.update()
        print("Contour Displace time: " + str(timeit.default_timer() - start_time) + " sec")

        return {'FINISHED'}

class OBJECT_OT_wm_set_weight_paint(bpy.types.Operator):
    bl_idname = "object.wm_set_weight_paint"
    bl_label = "Weight Paint"
    bl_description = ("")
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ob = context.object
        if ob.parent != None: ob = ob.parent
        bpy.context.view_layer.objects.active = ob
        ob.select_set(True)
        bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
        return {'FINISHED'}

### Sculpt Tools ###
from bl_ui.properties_paint_common import (
        UnifiedPaintPanel,
        brush_texture_settings,
        brush_texpaint_common,
        brush_mask_texture_settings,
        )

class View3DPanel:
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

class View3DPaintPanel(UnifiedPaintPanel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

### END Sculpt Tools ###

class WASPMED_PT_generate(View3DPaintPanel, bpy.types.Panel):
    bl_label = "Generate"
    bl_category = "Waspmed"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    #bl_options = {}
    #bl_context = "objectmode"

    '''
    @classmethod
    def poll(cls, context):
        return context.mode in {'OBJECT', 'EDIT_MESH'}
    '''

    @classmethod
    def poll(cls, context):
        try:
            ob = context.object
            if ob.parent != None:
                ob = ob.parent
            status = ob.waspmed_prop.status
            is_mesh = ob.type == 'MESH'
            return status == 5 and is_mesh and not context.object.hide_viewport
        except: return False

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)

        if context.mode == 'PAINT_WEIGHT':
            settings = self.paint_settings(context)
            col.template_ID_preview(settings, "brush", rows=3, cols=8)
            brush = settings.brush
            col.separator()
            self.prop_unified_size(col, context, brush, "size", slider=True, text="Radius")
            self.prop_unified_strength(col, context, brush, "strength", text="Strength")
        else:
            col.operator("object.wm_set_weight_paint", icon="BRUSH_DATA")

        col.separator()

        #col.operator("object.smooth_weight", icon="SMOOTHCURVE")
        col.operator("object.vertex_group_smooth", text="Smooth Weight", icon="SMOOTHCURVE")

        box = layout.box()
        col = box.column(align=True)
        #col.operator("view3d.ruler", text="Ruler", icon="ARROW_LEFTRIGHT")
        if context.mode == 'OBJECT':
            col.separator()
            col.operator("object.wm_add_measure_plane", text="Add Measure Plane", icon='MESH_PLANE')
            col.operator("object.wm_measure_circumference", text="Measure Circumference", icon='DRIVER_DISTANCE')
        col.separator()
        col.operator("screen.region_quadview", text="Toggle Quad View", icon='VIEW3D')
        col.separator()
        row = col.row(align=True)
        row.operator("ed.undo", icon='LOOP_BACK')
        row.operator("ed.redo", icon='LOOP_FORWARDS')
