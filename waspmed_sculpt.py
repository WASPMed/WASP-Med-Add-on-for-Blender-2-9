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

'''
def store_parameters(operator, ob):
    ob.tissue_tessellate.generator = operator.generator
    return ob

class waspmed_prop(bpy.types.PropertyGroup):
    patientID = bpy.props.StringProperty()
    status = bpy.props.IntProperty(default=0)
    zscale = bpy.props.FloatProperty(default=1)
    merge = bpy.props.BoolProperty()

class next(bpy.types.Operator):
    bl_idname = "object.next"
    bl_label = "Next"
    bl_description = ("")
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if context.object.waspmed_prop.patientID == "":
            context.object.waspmed_prop.patientID = context.object.name
        status = context.object.waspmed_prop.status
        bpy.ops.object.duplicate_move()
        context.object.waspmed_prop.status = status + 1
        return {'FINISHED'}

class back(bpy.types.Operator):
    bl_idname = "object.back"
    bl_label = "Back"
    bl_description = ("")
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        patientID = context.object.waspmed_prop.patientID
        status = context.object.waspmed_prop.status - 1
        for o in bpy.data.objects:
            if o.waspmed_prop.patientID == patientID and status == o.waspmed_prop.status:
                context.object = o
        return {'FINISHED'}
'''



class OBJECT_OT_wm_set_sculpt(bpy.types.Operator):
    bl_idname = "object.wm_set_sculpt"
    bl_label = "Sculpt"
    bl_description = ("")
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ob = context.object
        if ob.parent != None: ob = ob.parent
        bpy.context.view_layer.objects.active = ob
        ob.select_set(True)
        bpy.ops.object.mode_set(mode='SCULPT')
        return {'FINISHED'}


class OBJECT_OT_wm_set_draw(bpy.types.Operator):
    bl_idname = "object.wm_set_draw"
    bl_label = "Draw"
    bl_description = ("")
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        try:
            return context.object.mode == 'SCULPT'
        except: return False

    def execute(self, context):
        context.tool_settings.sculpt.brush.sculpt_tool = 'DRAW'
        return {'FINISHED'}


class OBJECT_OT_wm_set_smooth(bpy.types.Operator):
    bl_idname = "object.wm_set_smooth"
    bl_label = "Smooth"
    bl_description = ("")
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        try:
            return context.object.mode == 'SCULPT'
        except: return False

    def execute(self, context):
        context.tool_settings.sculpt.brush.sculpt_tool = 'SMOOTH'
        return {'FINISHED'}


class OBJECT_OT_wm_set_grab(bpy.types.Operator):
    bl_idname = "object.wm_set_grab"
    bl_label = "Grab"
    bl_description = ("")
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        try:
            return context.object.mode == 'SCULPT'
        except: return False

    def execute(self, context):
        context.tool_settings.sculpt.brush.sculpt_tool = 'GRAB'
        return {'FINISHED'}


### Sculpt Tools ###
from bl_ui.properties_paint_common import (
        UnifiedPaintPanel,
        brush_texture_settings,
        #brush_texpaint_common,
        brush_mask_texture_settings,
        )

class View3DPanel:
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

class View3DPaintPanel(UnifiedPaintPanel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

### END Sculpt Tools ###

class WASPMED_PT_sculpt(View3DPaintPanel, bpy.types.Panel):
#class waspmed_scan_panel(, bpy.types.View3DPaintPanel):
    bl_label = "Sculpt"
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
            return (status == 2 and is_mesh) and not context.object.hide_viewport
        except: return False

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)

        if context.mode == 'SCULPT':
            settings = self.paint_settings(context)
            #col.template_ID_preview(settings, "brush", rows=3, cols=8)
            brush = settings.brush
            col.separator()
            row = col.row(align=True)
            row.scale_y = 2
            row.operator("object.wm_set_draw", icon="OUTLINER_DATA_GP_LAYER")#, icon="BRUSH_SCULPT_DRAW")
            row.operator("object.wm_set_smooth", icon="MOD_SMOOTH")#, icon="BRUSH_SMOOTH")
            row.operator("object.wm_set_grab", icon="MOD_WARP")#"BRUSH_GRAB")
            #row.prop(context.tool_settings.sculpt.brush, 'sculpt_tool', icon_only = True, expand=True)
            col.prop(context.scene.tool_settings.unified_paint_settings, 'size')
            col.prop(context.scene.tool_settings.unified_paint_settings, 'strength')
        else:
            col.operator("object.wm_set_sculpt", icon="SCULPTMODE_HLT")

        col.separator()
        box = layout.box()
        col = box.column(align=True)

        #col.operator("view3d.ruler", text="Ruler", icon="ARROW_LEFTRIGHT")
        #col.separator()
        if context.mode == 'PAINT_WEIGHT':
            col.operator("object.wm_check_differences",
                            icon="ZOOM_SELECTED",
                            text="Check Differences Off")
        else:
            col.operator("object.wm_check_differences",
                            icon="ZOOM_SELECTED",
                            text="Check Differences On")
        if context.mode == 'OBJECT':
            col.separator()
            col.operator("object.wm_add_measure_plane", text="Add Measure Plane", icon='MESH_CIRCLE')
            col.operator("object.wm_measure_circumference", text="Measure Circumferences", icon='DRIVER_DISTANCE')
        col.separator()
        col.operator("screen.region_quadview", text="Toggle Quad View", icon='VIEW3D')
        col.separator()
        row = col.row(align=True)
        row.operator("ed.undo", icon='LOOP_BACK')
        row.operator("ed.redo", icon='LOOP_FORWARDS')
