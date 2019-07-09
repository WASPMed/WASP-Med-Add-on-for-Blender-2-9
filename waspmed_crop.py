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


import bpy
from mathutils import Vector
import numpy as np
from math import sqrt, radians, pi
import random, re


class OBJECT_OT_wm_crop_geometry(bpy.types.Operator):
    bl_idname = "object.wm_crop_geometry"
    bl_label = "Crop Geometry"
    bl_description = ("")
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        active_object = context.object
        selected = context.selected_objects
        ob = active_object.parent
        if ob == None: ob = active_object
        for o in bpy.data.objects: o.select_set(o == ob)
        context.view_layer.objects.active = ob
        patientID = ob.waspmed_prop.patientID
        status = ob.waspmed_prop.status
        for o in bpy.data.objects:
            id = o.waspmed_prop.patientID
            s = o.waspmed_prop.status
            if patientID == id and s == status-1:
                ob.data = o.to_mesh().copy()
        bpy.ops.object.mode_set(mode='EDIT')

        side = False
        planes = ["Plane X0", "Plane X1", "Plane Y0", "Plane Y1", "Plane Z0", "Plane Z1"]
        for plane_name in planes:
            try:
                bpy.ops.mesh.select_all(action='SELECT')
                plane = bpy.data.objects[plane_name]
                loc = plane.location
                nor = plane.data.polygons[0].normal# * plane.matrix_world
                matrix = plane.matrix_world
                matrix_new = matrix.to_3x3().inverted().transposed()
                nor = matrix_new @ nor
                nor.normalize()
                bpy.ops.mesh.bisect(plane_co=loc, plane_no=nor, use_fill=plane.waspmed_prop.plane_cap, clear_outer=True)
            except: pass

        bpy.ops.object.mode_set(mode='OBJECT')

        for o in bpy.data.objects:
            o.select_set(o in selected)
        context.view_layer.objects.active = active_object

        return {'FINISHED'}

class OBJECT_OT_wm_define_crop_planes(bpy.types.Operator):
    bl_idname = "object.wm_define_crop_planes"
    bl_label = "Define Crop Planes"
    bl_description = ("")
    bl_options = {'REGISTER', 'UNDO'}

    x_planes : bpy.props.BoolProperty(
        name="X Planes", default=True,
        description="Generate X Planes")
    y_planes : bpy.props.BoolProperty(
        name="Y Planes", default=True,
        description="Generate Y Planes")
    z_planes : bpy.props.BoolProperty(
        name="Z Planes", default=True,
        description="Generate Z Planes")

    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT':
            ob = context.object
            if ob.type == 'MESH': return True
            elif ob.type == 'EMPTY' and ob.parent != None: return True
            else: return False
        else: return False

    def draw(self, context):
        layout = self.layout
        #layout.label(text="Examples")
        ob = context.object
        col=layout.column(align=True)
        col.prop(self, "x_planes")
        col.prop(self, "y_planes")
        col.prop(self, "z_planes")

    def execute(self, context):
        active_object = context.object
        ob = active_object.parent
        if ob == None: ob = active_object

        if ob.type == 'EMPTY':
            empty = ob
            ob = empty.parent
            bpy.data.objects.remove(empty)
        for c in ob.children:
            #if c.type == 'EMPTY':
            bpy.data.objects.remove(c)

        patientID = ob.waspmed_prop.patientID
        status = ob.waspmed_prop.status
        for o in bpy.data.objects:
            id = o.waspmed_prop.patientID
            s = o.waspmed_prop.status
            if patientID == id and s == status-1:
                ob.data = o.to_mesh().copy()

        bb0 = Vector(ob.bound_box[0])
        bb1 = Vector(ob.bound_box[6])
        bb_origin = (bb0+bb1)/2
        bb_size = bb1-bb0

        alpha = 0.4

        planes = []

        # Planes X
        if self.x_planes:
            bpy.ops.mesh.primitive_plane_add(
                size=1000,
                location=(bb_origin.x - bb_size.x/2, bb_origin.y, bb_origin.z),
                rotation=(0, -pi/2, 0))
            plane_x0 = context.object
            plane_x0.name = "Plane X0"
            plane_x0.dimensions = ob.dimensions.zyx

            mat = bpy.data.materials.new(name="X Planes")
            context.object.data.materials.append(mat)
            context.object.active_material.diffuse_color = (1, 1, 1, alpha)

            bpy.ops.mesh.primitive_plane_add(
                size=1000,
                location=(bb_origin.x + bb_size.x/2, bb_origin.y, bb_origin.z),
                rotation=(0, pi/2, 0))
            plane_x1 = context.object
            plane_x1.name = "Plane X1"
            plane_x1.dimensions = ob.dimensions.zyx
            context.object.data.materials.append(mat)

            planes.append(plane_x0)
            planes.append(plane_x1)

            plane_x0.lock_location = plane_x1.lock_location = (False, True, True)
            plane_x0.lock_rotation = plane_x1.lock_rotation = (True, False, False)

        # Planes Y
        if self.y_planes:
            bpy.ops.mesh.primitive_plane_add(
                size=1000,
                location=(bb_origin.x, bb_origin.y - bb_size.y/2, bb_origin.z),
                rotation=(pi/2, 0, 0))
            plane_y0 = context.object
            plane_y0.name = "Plane Y0"
            plane_y0.dimensions = ob.dimensions.xzy

            mat = bpy.data.materials.new(name="Y Planes")
            context.object.data.materials.append(mat)
            context.object.active_material.diffuse_color = (0, 1, .5, alpha)

            bpy.ops.mesh.primitive_plane_add(
                size=1000,
                location=(bb_origin.x, bb_origin.y + bb_size.y/2, bb_origin.z),
                rotation=(-pi/2, 0,  0))
            plane_y1 = context.object
            plane_y1.name = "Plane Y1"
            plane_y1.dimensions = ob.dimensions.xzy
            #plane_y1.hide_select = True
            plane_y1.parent = ob
            context.object.data.materials.append(mat)

            planes.append(plane_y0)
            planes.append(plane_y1)

            plane_y0.lock_location = plane_y1.lock_location = (True, False, True)
            plane_y0.lock_rotation = plane_y1.lock_rotation = (False, True, False)

        # Planes Z
        if self.z_planes:
            bpy.ops.mesh.primitive_plane_add(
                size=1000,
                location=(bb_origin.x, bb_origin.y, bb_origin.z - bb_size.z/2),
                rotation=(0, pi, 0))
            plane_z0 = context.object
            plane_z0.name = "Plane Z0"
            plane_z0.dimensions = ob.dimensions.xyz

            mat = bpy.data.materials.new(name="Z Planes")
            context.object.data.materials.append(mat)
            context.object.active_material.diffuse_color = (0, .1, 1, alpha)

            bpy.ops.mesh.primitive_plane_add(
                size=1000,
                location=(bb_origin.x, bb_origin.y, bb_origin.z + bb_size.z/2),
                rotation=(0, 0, 0))
            plane_z1 = context.object
            plane_z1.name = "Plane Z1"
            plane_z1.dimensions = ob.dimensions.xyz
            context.object.data.materials.append(mat)

            planes.append(plane_z0)
            planes.append(plane_z1)

            plane_z0.lock_location = plane_z1.lock_location = (True, True, False)
            plane_z0.lock_rotation = plane_z1.lock_rotation = (False, False, True)

        for plane in planes:
            #c.draw_type = 'BOUNDS'
            plane.parent = ob
            #plane.show_transparent = True
            plane.show_wire = True
            plane.show_name = True
            plane.waspmed_prop.status = 4
            plane.waspmed_prop.plane_cap = "Z" not in plane.name
            plane.select_set(False)
        context.view_layer.objects.active = ob
        ob.select_set(True)
        return {'FINISHED'}

class OBJECT_OT_wm_define_crop_planes_old(bpy.types.Operator):
    bl_idname = "object.wm_define_crop_planes_old"
    bl_label = "Define Crop Planes"
    bl_description = ("")
    bl_options = {'REGISTER', 'UNDO'}

    x0 : bpy.props.FloatProperty(
        name="Trim X0", default=0.00, soft_min=0, soft_max=500,
        description="Trim X0")
    x1 : bpy.props.FloatProperty(
        name="Trim X1", default=0.00, soft_min=-500, soft_max=0,
        description="Trim X1")
    y0 : bpy.props.FloatProperty(
        name="Trim Y0", default=0.00, soft_min=0, soft_max=500,
        description="Trim Y0")
    y1 : bpy.props.FloatProperty(
        name="Trim Y1", default=0.00, soft_min=-500, soft_max=0,
        description="Trim Y1")
    z0 : bpy.props.FloatProperty(
        name="Trim Z0", default=0.00, soft_min=0, soft_max=500,
        description="Trim Z0")
    z1 : bpy.props.FloatProperty(
        name="Trim Z1", default=0.00, soft_min=-500, soft_max=0,
        description="Trim Z1")

    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT':
            ob = context.object
            if ob.type == 'MESH': return True
            elif ob.type == 'EMPTY' and ob.parent != None: return True
            else: return False
        else: return False

    def draw(self, context):
        layout = self.layout
        #layout.label(text="Examples")
        ob = context.object
        layout.label(text="Crop X")
        row=layout.row(align=True)
        row.prop(self, "x0", text="X0")
        row.prop(self, "x1", text="X1")
        layout.label(text="Crop Y")
        row=layout.row(align=True)
        row.prop(self, "y0", text="Y0")
        row.prop(self, "y1", text="Y1")
        layout.label(text="Crop Z")
        row=layout.row(align=True)
        row.prop(self, "z0", text="Z0")
        row.prop(self, "z1", text="Z1")

    def execute(self, context):
        ob = context.object
        if ob.type == 'EMPTY':
            empty = ob
            ob = empty.parent
            bpy.data.objects.remove(empty)
        for c in ob.children:
            #if c.type == 'EMPTY':
            bpy.data.objects.remove(c)

        patientID = ob.waspmed_prop.patientID
        status = ob.waspmed_prop.status
        for o in bpy.data.objects:
            id = o.waspmed_prop.patientID
            s = o.waspmed_prop.status
            if patientID == id and s == status-1:
                ob.data = o.to_mesh().copy()

        bb0 = Vector(ob.bound_box[0])
        bb1 = Vector(ob.bound_box[6])
        bb0 += Vector((self.x0, self.y0, self.z0))
        bb1 += Vector((self.x1, self.y1, self.z1))
        bb_origin = (bb0+bb1)/2
        #empty.location = bb_origin

        alpha = 0.4

        # Planes X
        bpy.ops.mesh.primitive_plane_add(
            size=1000,
            location=(bb_origin.x + bb0.x, bb_origin.y, bb_origin.z),
            rotation=(0, -pi/2, 0))
        plane_x0 = context.object
        plane_x0.name = "Plane X0"
        plane_x0.constraints.new(type='LIMIT_LOCATION')
        plane_x0.constraints[0].use_min_x = True
        plane_x0.constraints[0].min_x = bb0.x
        plane_x0.dimensions = ob.dimensions.zyx
        plane_x0.hide_select = True
        plane_x0.parent = ob

        mat = bpy.data.materials.new(name="Material")
        context.object.data.materials.append(mat)
        context.object.active_material.diffuse_color = (1, 1, 1, alpha)
        bpy.context.object.show_wire = True

        bpy.ops.mesh.primitive_plane_add(
            size=1000,
            location=(bb_origin.x - bb0.x, bb_origin.y, bb_origin.z),
            rotation=(0, pi/2, 0))
        plane_x1 = context.object
        plane_x1.name = "Plane X1"
        plane_x1.constraints.new(type='LIMIT_LOCATION')
        plane_x1.constraints[0].use_max_x = True
        plane_x1.constraints[0].max_x = bb1.x
        plane_x1.dimensions = ob.dimensions.zyx
        plane_x1.hide_select = True
        plane_x1.parent = ob
        context.object.data.materials.append(mat)
        #context.object.show_transparent = True
        bpy.context.object.show_wire = True

        # Planes Z
        bpy.ops.mesh.primitive_plane_add(
            size=1000,
            location=(bb_origin.x, bb_origin.y, bb_origin.z + bb0.z),
            rotation=(0, pi, 0))
        plane_z0 = context.object
        plane_z0.name = "Plane Z0"
        plane_z0.constraints.new(type='LIMIT_LOCATION')
        plane_z0.constraints[0].use_min_z = True
        plane_z0.constraints[0].min_z = bb0.z
        plane_z0.dimensions = ob.dimensions.xyz
        plane_z0.hide_select = True
        plane_z0.parent = ob

        mat = bpy.data.materials.new(name="Material")
        context.object.data.materials.append(mat)
        context.object.active_material.diffuse_color = (0, .1, 1, alpha)
        bpy.context.object.show_wire = True


        bpy.ops.mesh.primitive_plane_add(
            size=1000,
            location=(bb_origin.x, bb_origin.y, bb_origin.z - bb0.z),
            rotation=(0, 0, 0))
        plane_z1 = context.object
        plane_z1.name = "Plane Z1"
        plane_z1.constraints.new(type='LIMIT_LOCATION')
        plane_z1.constraints[0].use_max_z = True
        plane_z1.constraints[0].max_z = bb1.z
        plane_z1.dimensions = ob.dimensions.xyz
        plane_z1.hide_select = True
        plane_z1.parent = ob
        context.object.data.materials.append(mat)
        #context.object.show_transparent = True
        bpy.context.object.show_wire = True

        for c in ob.children:
            #c.draw_type = 'BOUNDS'
            c.select_set(False)
        context.view_layer.objects.active = ob
        ob.select_set(True)
        return {'FINISHED'}

class WASPMED_PT_crop(bpy.types.Panel):
    bl_label = "Crop"
    bl_category = "Waspmed"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    @classmethod
    def poll(cls, context):
        try:
            ob = context.object
            if ob.parent != None:
                ob = ob.parent
            status = ob.waspmed_prop.status
            is_mesh = ob.type == 'MESH'
            return status == 4 and is_mesh # and not context.object.hide
        except: return False

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.operator("object.wm_define_crop_planes", text="Setting Crop Planes", icon="SETTINGS")
        ob = context.object
        if ob.parent != None: ob = ob.parent
        planes = [plane for plane in ob.children if "Plane" in plane.name]

        separator = True
        for p in planes:
            if "0" in p.name or separator:
                col.separator()
            separator = "1" in p.name
            row = col.row(align=True)
            icon = "RADIOBUT_ON" if p == context.object else "RADIOBUT_OFF"
            #icon = "SPACE2" if p == context.object else "SPACE3"
            row.label(text=p.name, icon=icon)
            #row.prop(p, "select", text="")
            row.prop(p.waspmed_prop, "plane_cap", text="", icon="SNAP_FACE")
            row.prop(p, "hide_viewport", text="")
            row.prop(p, "hide_select", text="")
        col.separator()
        col.separator()
        try:
            col.operator("object.wm_crop_geometry", text="Crop Geometry", icon="MOD_DECIM")
            col.separator()
        except:
            pass
        box = layout.box()
        col = box.column(align=True)
        #col.operator("view3d.ruler", text="Ruler", icon="ARROW_LEFTRIGHT")
        #col.separator()
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
