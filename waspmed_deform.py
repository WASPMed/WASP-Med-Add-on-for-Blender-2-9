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
from math import sqrt, radians
import random


class OBJECT_OT_wm_add_lattice_to_object(bpy.types.Operator):
    bl_idname = "object.wm_add_lattice_to_object"
    bl_label = "Add Lattice"
    bl_description = ("")
    bl_options = {'REGISTER', 'UNDO'}

    locx : bpy.props.FloatProperty(
        name="Location X", default=0.00, soft_min=-180, soft_max=180,
        description="Location X")
    locy : bpy.props.FloatProperty(
        name="Location Y", default=0.00, soft_min=-180, soft_max=180,
        description="Location Y")
    locz : bpy.props.FloatProperty(
        name="Location Z", default=0.00, soft_min=-180, soft_max=180,
        description="Location Z")

    rotx : bpy.props.FloatProperty(
        name="Rotation X", default=0.00, soft_min=-180, soft_max=180,
        description="Rotation X")
    roty : bpy.props.FloatProperty(
        name="Rotation Y", default=0.00, soft_min=-180, soft_max=180,
        description="Rotation Y")
    rotz : bpy.props.FloatProperty(
        name="Rotation Z", default=0.00, soft_min=-180, soft_max=180,
        description="Rotation Z")

    dimx : bpy.props.IntProperty(
        name="Size X", default=400, soft_min=100, soft_max=1000,
        description="Size X")
    dimy : bpy.props.IntProperty(
        name="Size Y", default=300, soft_min=100, soft_max=1000,
        description="Size Z")
    dimz : bpy.props.IntProperty(
        name="Size Z", default=700, soft_min=100, soft_max=1000,
        description="Size Z")

    subu : bpy.props.IntProperty(
        name="U", default=3, soft_min=1, soft_max=10,
        description="Subdivisions in U")
    subv : bpy.props.IntProperty(
        name="V", default=3, soft_min=1, soft_max=10,
        description="Subdivisions in V")
    subw : bpy.props.IntProperty(
        name="W", default=5, soft_min=1, soft_max=10,
        description="Subdivisions in W")

    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT':
            ob = context.object
            if ob.type == 'MESH': return True
            elif ob.type == 'LATTICE' and ob.parent != None: return True
            else: return False
        else: return False

    def draw(self, context):
        layout = self.layout
        #layout.label(text="Examples")
        ob = context.object
        layout.label(text="Subdivisions")
        row=layout.row(align=True)
        row.prop(self, "subu", text="U")
        row.prop(self, "subv", text="V")
        row.prop(self, "subw", text="W")
        layout.label(text="Location")
        row=layout.row(align=True)
        row.prop(self, "locx", text="X")
        row.prop(self, "locy", text="Y")
        row.prop(self, "locz", text="Z")
        layout.label(text="Rotation")
        row=layout.row(align=True)
        row.prop(self, "rotx", text="X")
        row.prop(self, "roty", text="Y")
        row.prop(self, "rotz", text="Z")
        layout.label(text="Dimensions")
        row=layout.row(align=True)
        row.prop(self, "dimx", text="X")
        row.prop(self, "dimy", text="Y")
        row.prop(self, "dimz", text="Z")

    def execute(self, context):
        ob = context.object
        if ob.type == 'LATTICE':
            lattice = ob
            ob = lattice.parent
            bpy.data.objects.remove(lattice)
        for m in ob.modifiers:
            if m.type == 'LATTICE':
                ob.modifiers.remove(m)
        for c in ob.children:
            if c.type == 'LATTICE':
                bpy.data.objects.remove(c)
        bpy.ops.object.add(type='LATTICE')
        bpy.context.object.parent = ob
        rx = radians(self.rotx)
        ry = radians(self.roty)
        rz = radians(self.rotz)
        lattice = context.object
        lattice.location = (self.locx, self.locy, self.locz)
        lattice.rotation_euler = (rx, ry, rz)
        lattice.dimensions.xyz = (self.dimx,self.dimy,self.dimz)
        lattice.data.points_u = self.subu
        lattice.data.points_v = self.subv
        lattice.data.points_w = self.subw
        lattice.data.use_outside = True
        ob.modifiers.new(type='LATTICE', name="Lattice")
        ob.modifiers["Lattice"].object = lattice
        return {'FINISHED'}

class OBJECT_OT_wm_edit_lattice(bpy.types.Operator):
    bl_idname = "object.wm_edit_lattice"
    bl_label = "Edit Lattice"
    bl_description = ("")
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        try:
            ob = context.object
            is_lattice = ob.type == 'LATTICE'
            has_lattice_child = False
            for child in ob.children:
                if child.type == 'LATTICE' and ob.type == 'MESH':
                    has_lattice_child = True
            return is_lattice or has_lattice_child
        except: return False

    def execute(self, context):
        ob = context.object
        if ob.type == 'MESH':
            for child in ob.children:
                if child.type == 'LATTICE':
                    bpy.context.view_layer.objects.active = child
                    child.hide_viewport = False
                    child.select_set(True)
                    ob.select_set(False)
                    break
        bpy.ops.object.mode_set(mode='EDIT')
        return {'FINISHED'}

class OBJECT_OT_wm_rotate_sections(bpy.types.Operator):
    bl_idname = "object.wm_rotate_sections"
    bl_label = "Rotate Sections"
    bl_description = ("")
    bl_options = {'REGISTER', 'UNDO'}


    r0 : bpy.props.FloatProperty(
        name="Section 1", default=0.00, soft_min=-180, soft_max=180,
        description="Rotation of section 1")
    r1 : bpy.props.FloatProperty(
        name="Section 2", default=0.00, soft_min=-180, soft_max=180,
        description="Rotation of section 2")
    r2 : bpy.props.FloatProperty(
        name="Section 3", default=0.00, soft_min=-180, soft_max=180,
        description="Rotation of section 3")
    r3 : bpy.props.FloatProperty(
        name="Section 4", default=0.00, soft_min=-180, soft_max=180,
        description="Rotation of section 4")
    r4 : bpy.props.FloatProperty(
        name="Section 5", default=0.00, soft_min=-180, soft_max=180,
        description="Rotation of section 5")
    r5 : bpy.props.FloatProperty(
        name="Section 6", default=0.00, soft_min=-180, soft_max=180,
        description="Rotation of section 6")
    r6 : bpy.props.FloatProperty(
        name="Section 7", default=0.00, soft_min=-180, soft_max=180,
        description="Rotation of section 7")
    r7 : bpy.props.FloatProperty(
        name="Section 8", default=0.00, soft_min=-180, soft_max=180,
        description="Rotation of section 8")
    r8 : bpy.props.FloatProperty(
        name="Section 9", default=0.00, soft_min=-180, soft_max=180,
        description="Rotation of section 9")
    r9 : bpy.props.FloatProperty(
        name="Section 10", default=0.00, soft_min=-180, soft_max=180,
        description="Rotation of section 10")

    @classmethod
    def poll(cls, context):
        try:
            return context.object.type == 'LATTICE'
        except: return False

    def draw(self, context):
        layout = self.layout
        #layout.label(text="Examples")
        ob = context.object
        layout.label(text="Rotate Sections")
        col=layout.column(align=True)
        n_sections = min(ob.data.points_w, 10)
        property_names = ["r"+str(i) for i in range(n_sections)]
        for name in property_names:
            col.prop(self, name)

    def execute(self, context):
        ob = context.object
        nu, nv, nw = ob.data.points_u, ob.data.points_v, ob.data.points_w

        angles = [self.r0, self.r1, self.r2, self.r3, self.r4, self.r5, self.r6,
             self.r7, self.r8, self.r9]
        angles = [ radians(a) for a in angles]

        for i in range(nw):
            for u in range(nu):
                for v in range(nv):
                    for w in range(nw):
                        ob.data.points[w*nu*nv+ v*nu + u].select = w == nw-1-i
            bpy.ops.object.mode_set(mode="OBJECT")
            bpy.ops.object.mode_set(mode="EDIT")
            #bpy.ops.transform.rotate(value=angles[min(i,len(angles)-1)], axis=(0, 0, 1))
            #bpy.ops.transform.rotate(value=angles[min(i,len(angles)-1)], orient_axis='Z', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)))
            bpy.ops.transform.rotate(value=angles[min(i,len(angles)-1)])
            for p in ob.data.points: p.select = False
            bpy.ops.object.mode_set(mode="OBJECT")
            bpy.ops.object.mode_set(mode="EDIT")

        return {'FINISHED'}


class WASPMED_PT_deform(bpy.types.Panel):
#class waspmed_scan_panel(, bpy.types.View3DPaintPanel):
    bl_label = "Deform"
    bl_category = "Waspmed"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    #bl_options = {}
    #bl_context = "objectmode"

    #@classmethod
    #def poll(cls, context):
    #    return context.mode in {'OBJECT', 'EDIT_MESH'}

    @classmethod
    def poll(cls, context):
        try:
            ob = context.object
            if ob.parent != None:
                ob = ob.parent
            status = ob.waspmed_prop.status
            is_lattice = ob.type == 'LATTICE' and ob.parent != None
            is_mesh = ob.type == 'MESH'
            return ((status == 3 and is_mesh) or is_lattice) and not context.object.hide_viewport
        except: return False

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.operator("object.wm_add_lattice_to_object", text="Add Lattice", icon="MOD_LATTICE")
        col.separator()
        if context.mode != 'EDIT_LATTICE':
            col.operator("object.wm_edit_lattice", text="Edit Lattice", icon="LATTICE_DATA")
        else:
            col.operator("object.wm_rotate_sections", text="Twist", icon="FORCE_MAGNETIC")
            col.separator()
            col.operator("object.editmode_toggle", text="Object Mode", icon="OUTLINER_OB_LATTICE")
        col.separator()

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
