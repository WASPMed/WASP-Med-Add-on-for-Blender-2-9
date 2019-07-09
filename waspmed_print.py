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


class WASPMED_PT_print(bpy.types.Panel):
#class waspmed_scan_panel(, bpy.types.View3DPaintPanel):
    bl_label = "Print"
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
            is_mesh = ob.type == 'MESH'
            return status == 6 and is_mesh and not context.object.hide_viewport
        except: return False

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)


        col.label(text="Shell Thickness:")#, icon='MOD_WARP')
        col.prop(context.object.waspmed_prop, "min_thickness")
        col.prop(context.object.waspmed_prop, "max_thickness")
        col.separator()
        col.label(text="Profile:")
        md = context.object.modifiers["Profile"]

        row = col.row(align=True)
        row.prop(md, 'falloff_type', text='')
        row.prop(md, 'show_viewport', text='')
        if md.falloff_type == 'CURVE':
            col.template_curve_mapping(md, "map_curve")
        col.separator()

        col.label(text="Smooth:")#, icon='MOD_SMOOTH')
        row = col.row(align=True)
        #row.prop(context.object.waspmed_prop, "bool_smooth", icon='MOD_SMOOTH', text="")
        row.prop(context.object.waspmed_prop, "smooth_iterations", text="Steps")
        row.prop(context.object.waspmed_prop, "bool_smooth", text="", icon='MOD_SMOOTH')
        col.separator()

        col.label(text="Auto Crop:")#, icon='MOD_DECIM')
        row = col.row(align=True)
        row.prop(context.object.waspmed_prop, "trim_bottom", text="Offset")
        row.prop(context.object.waspmed_prop, "bool_trim_bottom", icon='MOD_DECIM', text="")
        col.separator()

        '''
        col.separator()
        col.label(text="Export:", icon='EXPORT')
        row = col.row(align=True)
        row.operator("export_mesh.stl", text="STL")
        row.operator("export_scene.obj", text="OBJ")
        col.separator()
        #col.separator()
        '''

        box = layout.box()
        col = box.column(align=True)
        #col.label(text="Utils:")
        #col.operator("view3d.ruler", text="Ruler", icon="ARROW_LEFTRIGHT")
        if context.mode == 'OBJECT' and False:
            col.separator()
            col.operator("object.add_measure_plane", text="Add Measure Plane", icon='MESH_PLANE')
            col.operator("object.measure_circumference", text="Measure Circumference", icon='DRIVER_DISTANCE')
        col.separator()
        col.operator("screen.region_quadview", text="Toggle Quad View", icon='VIEW3D')
        col.separator()
        row = col.row(align=True)
        row.operator("ed.undo", icon='LOOP_BACK')
        row.operator("ed.redo", icon='LOOP_FORWARDS')
