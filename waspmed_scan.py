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


import bpy, bmesh
from mathutils import Vector
import numpy as np
from math import sqrt, radians
import random

status_list = ["scan", "remesh", "sculpt", "deform", "crop", "create","generate", "print"]

#def store_parameters(operator, ob):
#    ob.tissue_tessellate.generator = operator.generator
#    return ob


def get_patient(ob):
    while ob.parent: ob = ob.parent
    if ob.type == 'MESH': return ob
    else: return False

def get_status(ob):
    try: return get_patient(ob).waspmed_prop.status
    except: return False

def get_patientID(ob):
    try: return get_patient(ob).waspmed_prop.patientID
    except: return False


def xray_shading(bool_xray):
    my_areas = bpy.context.screen.areas
    #my_shading = 'WIREFRAME'  # 'WIREFRAME' 'SOLID' 'MATERIAL' 'RENDERED'
    for area in my_areas:
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.shading.show_xray = bool_xray

def update_smooth(self, context):
    ob = context.object
    try:
        mod = ob.modifiers["CorrectiveSmooth"]
    except:
        ob.modifiers.new(type='CORRECTIVE_SMOOTH', name="CorrectiveSmooth")
        mod = ob.modifiers["CorrectiveSmooth"]
        bpy.ops.object.modifier_move_up(modifier = mod.name)
    mod.vertex_group = "Smooth"
    mod.invert_vertex_group = True
    mod.use_only_smooth = True
    mod.use_pin_boundary = True
    mod.iterations = ob.waspmed_prop.smooth_iterations
    mod.factor = 1
    mod.show_viewport = ob.waspmed_prop.bool_smooth


def update_trim_bottom(self, context):
    if True:
        margin = 10
        ob = context.object
        if ob.waspmed_prop.status < 6: return
        min_x, min_y, min_z = max_x, max_y, max_z = ob.matrix_world @ ob.data.vertices[0].co
        init_z = True
        for v in ob.data.vertices:
            # store vertex world coordinates
            world_co = ob.matrix_world @ v.co
            min_x = min(min_x, world_co[0])-margin
            min_y = min(min_y, world_co[1])-margin
            max_x = max(max_x, world_co[0])+margin
            max_y = max(max_y, world_co[1])+margin
            try:
                if ob.vertex_groups["Smooth"].weight(v.index) > 0.5:
                    if init_z:
                        min_z = max_z = world_co[2]
                        init_z = False
                    else:
                        min_z = min(min_z, world_co[2])
                        max_z = max(max_z, world_co[2])
            except:
                pass
        loc = (
            (min_x + max_x)/2,
            (min_y + max_y)/2,
            (min_z + max_z)/2,
            )
        try:
            box = bpy.data.objects["Crop_Box"]
            box.location = loc
        except:
            bpy.ops.mesh.primitive_cube_add(location=loc,
                size = max(max_x - min_x, max_y - min_y)/100 + 2)
            box = bpy.context.object
        box.dimensions[2] = max_z - min_z + ob.waspmed_prop.trim_bottom*2
        box.name = "Crop_Box"
        bpy.context.view_layer.objects.active = ob
        ob.select_set(True)
        box.display_type = 'WIRE'
        box.parent = ob
        box.hide_select = True
        box.hide_viewport = True
        box.select_set(False)
        try:
            mod = ob.modifiers["Crop"]
        except:
            ob.modifiers.new(type="BOOLEAN", name="Crop")
            mod = ob.modifiers["Crop"]
        mod.object = box
        mod.operation = 'INTERSECT'
        mod.double_threshold = 0
        #mod.solver = 'CARVE'
        if ob.waspmed_prop.bool_trim_bottom:
            mod.show_viewport = False
            #context.scene.update()
        mod.show_viewport = ob.waspmed_prop.bool_trim_bottom

    #except:
    #    pass

def update_thickness(self, context):
    try:
        ob = bpy.context.object
        mod = ob.modifiers['Solidify']
        min_t = ob.waspmed_prop.min_thickness
        max_t = ob.waspmed_prop.max_thickness
        if min_t == 0:
            ob.modifiers['Mask'].vertex_group = "Smooth"
            ob.modifiers['Mask'].show_viewport = True
            ob.modifiers["Mask"].show_render = True
        else:
            ob.modifiers['Mask'].show_viewport = False
            ob.modifiers["Mask"].show_render = False
        mod.thickness = max_t
        mod.thickness_vertex_group = min_t / max_t
        mod.use_even_offset = True
    except:
        pass

def update_crop(self, context):
    try:
        bpy.ops.object.crop_geometry()
    except:
        pass

class waspmed_object_prop(bpy.types.PropertyGroup):
    patientID : bpy.props.StringProperty()
    status : bpy.props.IntProperty(default=0)
    zscale : bpy.props.FloatProperty(default=1)
    merge : bpy.props.BoolProperty()
    min_thickness : bpy.props.FloatProperty(
        name="Min", default=3, min=0.0, soft_max=10,
        description="Max Thickness",
        unit = 'LENGTH',
        update = update_thickness
        )
    max_thickness : bpy.props.FloatProperty(
        name="Max", default=6, min=0.01, soft_max=10,
        description="Max Thickness",
        unit = 'LENGTH',
        update = update_thickness
        )
    bool_trim_bottom : bpy.props.BoolProperty(
        name = "Trim",
        description = "Create a flat bottom",
        default = False,
        update = update_trim_bottom
        )
    trim_bottom : bpy.props.FloatProperty(
        name="Distance", default=5, min=0.01, soft_max=50,
        description="Trim distance for the bottom",
        unit = 'LENGTH',
        update = update_trim_bottom
        )
    bool_smooth : bpy.props.BoolProperty(
        name = "Smooth",
        description = "Smooth body",
        default = False,
        update = update_smooth
        )
    smooth_iterations : bpy.props.IntProperty(
        name="Iterations", default=100, min=0, soft_max=1000,
        description="Corrective Smooth Iterations",
        update = update_smooth
        )
    plane_cap : bpy.props.BoolProperty(
        name="Cap", default=False,
        description="Fill the section area",
        update = update_crop
        )


class waspmed_scene_prop(bpy.types.PropertyGroup):
    do_setup : bpy.props.BoolProperty(default=True)


class OBJECT_OT_wm_add_measure_plane(bpy.types.Operator):
    bl_idname = "object.wm_add_measure_plane"
    bl_label = "Add Circumference"
    bl_description = ("Generate a section plane object in order to evaluate the local circumference")
    bl_options = {'REGISTER', 'UNDO'}

    thickness : bpy.props.FloatProperty(
        name="Thickness", default=5, min=0.0001, soft_max=20,
        description="Wireframe modifier thickness",
        unit = 'LENGTH'
        )

    @classmethod
    def poll(cls, context):
        try:
            ob = get_patient(context.object)
            if get_status(ob) > 0:
                return not ob.hide_viewport
            else: return False
        except: return False

    def execute(self, context):
        ob = get_patient(context.object)
        size = ob.dimensions.length
        bpy.ops.mesh.primitive_plane_add(size=size, location=(0, 0, 0))
        plane = context.object
        bpy.ops.object.modifier_add(type='BOOLEAN')
        plane.modifiers[-1].object = ob
        plane.modifiers[-1].operation = 'INTERSECT'
        bpy.ops.object.modifier_add(type='WIREFRAME')
        plane.modifiers[-1].use_boundary = True
        plane.modifiers[-1].thickness = self.thickness
        plane.modifiers[-1].use_even_offset = False

        try:
            mat = bpy.data.materials["Circumference"]
        except:
            mat = bpy.data.materials.new(name="Circumference")
            mat.diffuse_color = (0, 1, .5, 0.8)
        plane.data.materials.append(mat)
        plane.parent = ob
        plane.name = "Circumference"
        return {'FINISHED'}


class OBJECT_OT_wm_measure_circumference(bpy.types.Operator):
    bl_idname = "object.wm_measure_circumference"
    bl_label = "Measure Circumference"
    bl_description = ("Recompute the circumference of the selected section plane")
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        try:
            ob = context.object
            if "Circumference" in ob.name:
                return not ob.hide_viewport
            else: return False
        except: return False

    def execute(self, context):
        ob = context.object
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        show_modifiers = []
        for m in ob.modifiers:
            show_modifiers.append(m.show_viewport)
            if m.type != 'BOOLEAN': m.show_viewport = False
        me = ob.to_mesh()
        for m, show in zip(ob.modifiers, show_modifiers): m.show_viewport = show
        length = 0
        bm = bmesh.new()
        bm.from_mesh(me)
        for e in bm.edges: length += e.calc_length()
        #length *= bpy.context.scene.unit_settings.scale_length

        if bpy.context.scene.unit_settings.system == 'METRIC':
            unit = bpy.context.scene.unit_settings.length_unit
            unit_dict = {
                'ADAPTIVE': 'm',
                'KILOMETERS': 'km',
                'METERS': 'm',
                'CENTIMETERS': 'cm',
                'MILLIMETERS': 'mm',
                'MICROMETERS': 'μm'
            }
            unit_str = unit_dict[unit]
        else: unit_str = ""
        ob.name = ob.name.split(":")[0] + ": {:.2f} {}".format(length, unit_str)
        ob.show_name = True
        return {'FINISHED'}

class MESH_OT_wm_cap_holes(bpy.types.Operator):
    bl_idname = "mesh.wm_cap_holes"
    bl_label = "Cap Holes"
    bl_description = ("")
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        try: return not context.object.hide_viewport
        except: return False

    def execute(self, context):
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_non_manifold(
            extend=False, use_wire=False, use_multi_face=False,
            use_non_contiguous=False, use_verts=False)
        bpy.ops.mesh.edge_face_add()
        bpy.ops.mesh.quads_convert_to_tris(
            quad_method='BEAUTY', ngon_method='BEAUTY')
        bpy.ops.object.mode_set(mode='OBJECT')
        return {'FINISHED'}


class OBJECT_OT_wm_next(bpy.types.Operator):
    bl_idname = "object.wm_next"
    bl_label = "Next"
    bl_description = ("")
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        try:
            ob = get_patient(context.object)
            status = get_status(ob)
            if status == 5 and len(ob.vertex_groups) == 0:
                return False
            if ob.hide_viewport: #not bpy.context.object.is_visible(bpy.context.scene):
                return False
            #if ob.parent != None:
            #    ob = ob.parent
            if status < len(status_list)-1:
                return True
            else: return False
        except:
            return False

    def execute(self, context):
        old_ob = get_patient(context.object)

        # hide and deselect childrens
        for child in old_ob.children:
            child.hide_viewport = True
            child.select_set(False)

        old_ob.hide_viewport = False
        old_ob.select_set(True)
        context.view_layer.objects.active = old_ob

        bpy.ops.object.mode_set(mode='OBJECT')

        '''
        # if crop planes are selected
        if old_ob.waspmed_prop.status == 4 and old_ob.parent != None:
            old_ob.hide_viewport = True
            old_ob.select_set(False)
            old_ob = old_ob.parent
            context.view_layer.objects.active = old_ob

        if old_ob.type != 'MESH' and old_ob.parent != None:
            old_ob.hide_viewport = True
            old_ob.select_set(False)
            old_ob = old_ob.parent
            context.view_layer.objects.active = old_ob

        old_ob.hide_viewport = False
        bpy.ops.object.mode_set(mode='OBJECT')
        '''

        init_object = False
        if old_ob.waspmed_prop.patientID == "":
            init_object = True
            old_ob.waspmed_prop.patientID = old_ob.name
        status = old_ob.waspmed_prop.status
        patientID = old_ob.waspmed_prop.patientID

        #ob = None
        # check for existing nex step and delete them
        for o in bpy.data.objects:
            if o.waspmed_prop.patientID == patientID and status+1 == o.waspmed_prop.status:
                for child in o.children: bpy.data.objects.remove(child)
                bpy.data.objects.remove(o)
                '''
                if status+1 != 3:
                    for child in o.children: bpy.data.objects.remove(child)
                    bpy.data.objects.remove(o)
                else:
                    for child in o.children: child.hide_viewport = False
                    o.data = old_ob.data
                    context.view_layer.objects.active = o
                    o.select_set(True)
                    o.hide_viewport = False
                    ob = o
                '''

        # set X-ray for cropping planes
        '''
        if status+1 == 4:
            xray_shading(True)
        if status+1 == 5:
            xray_shading(False)
        '''

        # generate new next status
        #new_ob = old_ob.copy()
        #if ob == None:
        ob = context.object
        ob.select_set(True)
        context.view_layer.objects.active = ob
        old_status = status_list[status]
        next_status = status_list[status+1]
        if status == 0 and init_object:
            ob.name = "00_" + patientID + "_" + old_status
            user_col = ob.users_collection[0]
            bool_new_col = len(user_col.objects) > 1
            if not bool_new_col:
                try:
                    user_col.name = patientID
                except:
                    bool_new_col = True
            if bool_new_col:
                col = bpy.data.collections.new(patientID)
                bpy.context.scene.collection.children.link(col)
                col.objects.link(ob)
                try: bpy.context.scene.collection.objects.unlink(ob)
                except: pass
                for c in bpy.data.collections:
                    if c != col and ob in c.objects: c.objects.unlink(ob)
            #bpy.context.collection.name = patientID
        if status == 5:
            bpy.ops.object.wm_weight_thickness()
            new_ob = context.object
            update_smooth(new_ob, context)
            new_ob.modifiers.new(type='MASK', name="Mask")
            bpy.ops.object.modifier_move_up(modifier = "Mask")
            #new_ob.modifiers["Mask"].vertex_group = "Smooth"

            #new_ob.modifiers.new(type='CORRECTIVE_SMOOTH', name="CorrectiveSmooth")
            #bpy.ops.object.modifier_move_up(modifier = new_ob.modifiers[-1].name)
            new_ob.modifiers.new(type="BOOLEAN", name="Crop")

            bpy.context.object.waspmed_prop.patientID = patientID
        else:
            bpy.ops.object.convert(target='MESH', keep_original=True)
            #bpy.ops.object.duplicate_move()
        bpy.ops.object.mode_set(mode='OBJECT')
        try:
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        except:
            pass
        new_ob = context.object

        new_ob.waspmed_prop.status = status + 1
        new_ob.name = str(status+1).zfill(2) + "_" + patientID + "_" + next_status
        #for o in bpy.data.objects:
        #    if o != new_ob and o not in new_ob.children: o.hide_viewport = True

        # change mode
        if new_ob.waspmed_prop.status == 2:
            bpy.ops.object.mode_set(mode='SCULPT')
            bpy.context.scene.tool_settings.sculpt.use_symmetry_x = False
        elif new_ob.waspmed_prop.status == 5:
            bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
            new_ob.vertex_groups.new(name="Group")
            bpy.data.brushes["Mix"].spacing = 4
        else: bpy.ops.object.mode_set(mode='OBJECT')

        if status != 5:
            for vg in new_ob.vertex_groups: new_ob.vertex_groups.remove(vg)
            #for mod in new_ob.modifiers:
                #new_ob.modifiers.remove(mod)
                #try: bpy.ops.object.modifier_apply(apply_as='DATA', modifier=mod.name)
                #except: pass
            #bpy.ops.object.convert(target='MESH')

        old_ob.hide_viewport = True
        old_ob.select_set(False)
        new_ob.select_set(True)
        return {'FINISHED'}

class OBJECT_OT_wm_back(bpy.types.Operator):
    bl_idname = "object.wm_back"
    bl_label = "Back"
    bl_description = ("")
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        try:
            visible = context.object.waspmed_prop.status > 0
            if bpy.context.object.hide_viewport:
                return False
            if not visible:
                try: visible = context.object.parent.waspmed_prop.status > 0
                except: pass
            return visible
        except: return False

    def execute(self, context):
        '''
        ob = context.object
        bpy.ops.object.mode_set(mode='OBJECT')
        if ob.type == 'LATTICE' or "Circumference" in ob.name:
            try:
                ob.hide_viewport = True
                ob = context.object.parent
            except:
                return {'FINISHED'}
        '''

        old_ob = get_patient(context.object)
        old_ob.hide_viewport = True
        old_ob.select_set(False)
        for child in old_ob.children:
            child.hide_viewport = True
            child.select_set(False)
        patientID = old_ob.waspmed_prop.patientID
        status = old_ob.waspmed_prop.status - 1

        # set X-ray for cropping planes
        '''
        if status == 4:
            xray_shading(True)
        if status == 3:
            xray_shading(False)
        '''

        for o in bpy.data.objects:
            ob = get_patient(o)
            if ob.waspmed_prop.patientID == patientID and status == ob.waspmed_prop.status:
                bpy.context.view_layer.objects.active = ob
                ob.select_set(True)
                ob.hide_viewport = False
                #ob = o
                if ob.waspmed_prop.status == 2:
                    bpy.ops.object.mode_set(mode='SCULPT')
                elif ob.waspmed_prop.status == 5:
                    bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
                else: bpy.ops.object.mode_set(mode='OBJECT')
                for child in ob.children: child.hide_viewport = False
            '''
            else:
                try:
                    o.select_set(False)
                    o.hide_viewport = True
                except: pass
            '''


        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        if context.object.waspmed_prop.status != 3:
            col.label(text="This will delete changes to the model.", icon="ERROR")
            col.label(text="Do you want to continue?")

    def invoke(self, context, event):
        if context.object.waspmed_prop.status == 3:
            return self.execute(context)
        #return context.window_manager.invoke_confirm(self, event)
        else: return context.window_manager.invoke_props_dialog(self)

class OBJECT_OT_wm_rebuild_mesh(bpy.types.Operator):
    bl_idname = "object.wm_rebuild_mesh"
    bl_label = "Rebuild Mesh"
    bl_description = ("")
    bl_options = {'REGISTER', 'UNDO'}

    detail : bpy.props.IntProperty(
        name="Detail", default=7, soft_min=3, soft_max=10,
        description="Octree Depth")

    @classmethod
    def poll(cls, context):
        try: return not context.object.hide_viewport
        except: return False

    def execute(self, context):
        '''
        ob = context.object
        patientID = ob.waspmed_prop.patientID
        status = ob.waspmed_prop.status
        if status > 0:
            for o in bpy.data.objects:
                if o.waspmed_prop.patientID == patientID:
                    if o.waspmed_prop.status == 0:
                        o.hide_viewport = False
                        o.select_set(True)
                        context.view_layer.objects.active = o
        '''
        bpy.ops.object.wm_back()
        bpy.ops.object.wm_next()

        bpy.ops.object.modifier_add(type='REMESH')
        bpy.context.object.modifiers["Remesh"].mode = 'SMOOTH'
        bpy.context.object.modifiers["Remesh"].octree_depth = self.detail
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Remesh")
        return {'FINISHED'}


class OBJECT_OT_wm_auto_origin(bpy.types.Operator):
    bl_idname = "object.wm_auto_origin"
    bl_label = "Center Model"
    bl_description = ("Center the 3D model automatically")
    bl_options = {'REGISTER', 'UNDO'}

    rotx : bpy.props.FloatProperty(
        name="Rotation X", default=0.00, soft_min=-180, soft_max=180,
        description="Rotation X")
    roty : bpy.props.FloatProperty(
        name="Rotation Y", default=0.00, soft_min=-180, soft_max=180,
        description="Rotation Y")
    rotz : bpy.props.FloatProperty(
        name="Rotation Z", default=-0.00, soft_min=-180, soft_max=180,
        description="Rotation Z")

    @classmethod
    def poll(cls, context):
        try: return not context.object.hide_viewport
        except: return False

    def execute(self, context):
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS')
        bpy.ops.object.location_clear(clear_delta=False)
        bpy.ops.view3d.view_selected(use_all_regions=False)
        rx = radians(self.rotx)
        ry = radians(self.roty)
        rz = radians(self.rotz)
        ob = context.object
        ob.rotation_euler = (rx, ry, rz)
        #ob.waspmed_prop.patientID = ob.name
        return {'FINISHED'}


def delete_all():
    for o in bpy.data.objects:
        bpy.data.objects.remove(o)

def set_mm():
    #for s in bpy.data.screens:
    #    for a in s.areas:
    #        if a.type == 'OUTLINER':
    #            a.spaces[0].display_mode = 'VISIBLE_LAYERS'
    bpy.context.scene.unit_settings.length_unit = 'MILLIMETERS'
    bpy.context.scene.unit_settings.scale_length = 0.001
    bpy.context.space_data.overlay.grid_scale = 0.001


def set_clipping_planes():
    bpy.context.space_data.lens = 50
    bpy.context.space_data.clip_start = 1
    bpy.context.space_data.clip_end = 1e+006

class OBJECT_OT_wm_check_differences(bpy.types.Operator):
    bl_idname = "object.wm_check_differences"
    bl_label = "Check Differences"
    bl_description = ("Check the differences with the original model")
    bl_options = {'REGISTER', 'UNDO'}

    max_dist : bpy.props.FloatProperty(
        name="Max Distance", default=5, soft_min=0, soft_max=50,
        description="Max Distance", unit='LENGTH')

    @classmethod
    def poll(cls, context):
        try:
            ob = get_patient(context.object)
            return ob.waspmed_prop.status != 0
        except: return False

    def execute(self, context):
        ob = get_patient(context.object)
        patientID = ob.waspmed_prop.patientID
        status = ob.waspmed_prop.status
        try:
            vg = ob.vertex_groups["Proximity"]
        except:
            vg = ob.vertex_groups.new(name="Proximity")
        for i in range(len(ob.data.vertices)):
            vg.add([i], 1, 'ADD')
        mod = None
        for m in ob.modifiers:
            if m.type == "VERTEX_WEIGHT_PROXIMITY":
                mod = m
        if mod == None: mod = ob.modifiers.new(
                                name="Differences",
                                type="VERTEX_WEIGHT_PROXIMITY"
                                )
        mod.vertex_group = vg.name
        mod.max_dist = self.max_dist
        for o in bpy.data.objects:
            o_patientID = o.waspmed_prop.patientID
            o_status = o.waspmed_prop.status
            if o_patientID == patientID and o_status == 0:
                mod.target = o
        if mod.target == None:
            self.report({'ERROR'}, "Can't find original scan model")
            return {'CANCELLED'}
        mod.proximity_mode = 'GEOMETRY'
        mod.proximity_geometry = {'FACE'}
        bpy.ops.paint.weight_paint_toggle()
        if context.mode == 'OBJECT' and status == 2:
            bpy.ops.object.mode_set(mode='SCULPT')
        return {'FINISHED'}



class SCENE_OT_wm_setup(bpy.types.Operator):
    bl_idname = "scene.wm_setup"
    bl_label = "Setup"
    bl_description = ("Reset the scene")
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        delete_all()
        set_mm()
        set_clipping_planes()
        context.scene.waspmed_prop.do_setup = False
        for brush in bpy.data.brushes:
            brush.spacing = 5
        for area in bpy.context.window.screen.areas:
            if area.type == 'OUTLINER':
                area.spaces[0].show_restrict_column_viewport = True
                area.spaces[0].show_restrict_column_select = True
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


class WASPMED_PT_progress(View3DPaintPanel, bpy.types.Panel):
#class waspmed_scan_panel(, bpy.types.View3DPaintPanel):
    bl_label = "Waspmed Progress"
    bl_category = "Waspmed"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    #bl_options = {}
    #bl_context = "objectmode"

    '''
    @classmethod
    def poll(cls, context):
        try:
            return bpy.context.object.is_visible(bpy.context.scene)
            #return context.object.waspmed_prop.status == 0
        except: return False
    '''
    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        if context.scene.waspmed_prop.do_setup:
            col.operator("scene.wm_setup", icon="FILE_NEW", text="Start")
            col.separator()
        else:
            try:
                if context.object.parent:
                    patient_name = context.object.parent.waspmed_prop.patientID
                else:
                    patient_name = context.object.waspmed_prop.patientID
                col.label(text=patient_name, icon="OUTLINER_OB_ARMATURE")
            except: col.label(text="Import new Patient",
                icon="INFO")
            if context.object != None:
                col.separator()
                row = col.row(align=True)
                row.operator("object.wm_back", icon='BACK')#, text="")
                if context.object.waspmed_prop.status == 7:
                    row.operator("export_mesh.stl", icon='EXPORT')#, text="")
                #elif context.object.waspmed_prop.status == 6:
                #    row.operator("object.convert", icon='EXPORT')#, text="")
                else:
                    row.operator("object.wm_next", icon='FORWARD')#, text="")

class WASPMED_PT_scan(View3DPaintPanel, bpy.types.Panel):
#class waspmed_scan_panel(, bpy.types.View3DPaintPanel):
    bl_label = "3D Scan"
    bl_category = "Waspmed"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    #bl_options = {}
    #bl_context = "objectmode"


    @classmethod
    def poll(cls, context):
        try:
            ob = get_patient(context.object)
            #if ob.parent != None:
            #    ob = ob.parent
            status = ob.waspmed_prop.status
            is_mesh = ob.type == 'MESH'
            return (status < 2 and is_mesh) and not ob.hide
        except: return True


    def draw(self, context):
        try:
            ob = get_patient(context.object)
            status = ob.waspmed_prop.status
        except:
            status = 0
        layout = self.layout
        col = layout.column(align=True)

        if status != 1:
            col.label(text="Import Patient:", icon="OUTLINER_OB_ARMATURE")
            row = col.row(align=True)
            row.operator("import_scene.obj", text="OBJ")
            row.operator("import_mesh.stl", text="STL")
            col.separator()
            col.operator("object.wm_auto_origin", icon='SHADING_BBOX')
            col.separator()
        #col.label(text="Fix model", icon='ZOOM_SELECTED')
        #col.operator("mesh.cap_holes", text="Cap Holes")
        if status == 1:
            col.operator("object.wm_rebuild_mesh", icon="MOD_REMESH", text="Auto Remesh")
            col.separator()
        '''
        try:
            settings = self.paint_settings(context)
            col.template_ID_preview(settings, "brush", rows=3, cols=8)
            brush = settings.brush
            self.prop_unified_size(col, context, brush, "size", slider=True, text="Radius")
            self.prop_unified_strength(col, context, brush, "strength", text="Strength")
        except: pass
        '''
        #col.template_preview(bpy.data.textures['.hidden'], show_buttons=False)
        col.separator()


        box = layout.box()
        col = box.column(align=True)
        #col.label(text="Utils:")
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
            col.operator("object.wm_measure_circumference", text="Measure Circumference", icon='DRIVER_DISTANCE')
        col.separator()
        col.operator("screen.region_quadview", text="Toggle Quad View", icon='VIEW3D')
        col.separator()
        row = col.row(align=True)
        row.operator("ed.undo", icon='LOOP_BACK')
        row.operator("ed.redo", icon='LOOP_FORWARDS')
