import bpy


class VIEW_OT_set_active_obj(bpy.types.Operator):
    """ Click to select obj and set as active obj
Ctrl to deselect"""
    bl_idname = "view.set_active_obj"
    bl_label = "Set Active Object"
    bl_options = {'INTERNAL', 'UNDO'}
    # bl_options = {'INTERNAL'}

    obj_name: bpy.props.StringProperty(name="Name")

    def invoke(self, context, event):
        obj = bpy.data.objects[self.obj_name]

        if event.ctrl:
            obj.select_set(False)
        else:
            context.view_layer.objects.active = obj
            obj.select_set(True)

        return {'FINISHED'}


# select obj by lightgroup
class VIEW_OT_select_obj_by_lightgroup(bpy.types.Operator):
    """ Select obj by lightgroup """
    bl_idname = "view.select_obj_by_lightgroup"
    bl_label = "Select Object by Lightgroup"
    bl_options = {'INTERNAL', 'UNDO'}

    lightgroup: bpy.props.StringProperty(name="Lightgroup")

    def invoke(self, context, event):
        for obj in bpy.data.objects:
            if obj.lightgroup == self.lightgroup:
                obj.select_set(True)

        return {'FINISHED'}


# set lightgroup object visibility
class VIEW_OT_toggle_lightgroup_visibility(bpy.types.Operator):
    """ Toggle lightgroup object visibility """
    bl_idname = "view.toggle_lightgroup_visibility"
    bl_label = "Toggle Lightgroup Visibility"
    bl_options = {'INTERNAL', 'UNDO'}

    lightgroup: bpy.props.StringProperty(name="Lightgroup")

    def invoke(self, context, event):
        from .ui import get_obj_list_in_lightgroup
        fit_list = get_obj_list_in_lightgroup(self.lightgroup)
        vis = not fit_list[0].hide_viewport

        for obj in fit_list:
            obj.hide_viewport = vis
            obj.hide_render = vis

        return {'FINISHED'}


# solo lightgroup object
class VIEW_OT_solo_lightgroup_object(bpy.types.Operator):
    bl_idname = "view.solo_lightgroup_object"
    bl_label = "Solo Lightgroup Object"
    bl_option = {'INTERNAL', 'UNDO'}

    lightgroup: bpy.props.StringProperty(name="Lightgroup")

    def execute(self, context):
        # get all lightgroup objects
        from .ui import get_obj_list_in_lightgroup
        for lightgroup_item in context.view_layer.lightgroups:
            obj_list = get_obj_list_in_lightgroup(lightgroup_item.name)
            if lightgroup_item.name != self.lightgroup:
                for obj in obj_list:
                    obj.hide_viewport = True
                    obj.hide_render = True
            else:
                for obj in obj_list:
                    obj.hide_viewport = False
                    obj.hide_render = False

        return {'FINISHED'}


# solo light in lightgroup
class VIEW_OT_solo_light_in_lightgroup(bpy.types.Operator):
    bl_idname = "view.solo_light_in_lightgroup"
    bl_label = "Solo Light in Lightgroup"
    bl_option = {'INTERNAL', 'UNDO'}

    lightgroup: bpy.props.StringProperty(name="Lightgroup")
    obj_name: bpy.props.StringProperty(name="Object Name")

    def execute(self, context):
        # get objects with lightgroup
        from .ui import get_obj_list_in_lightgroup
        fit_list = get_obj_list_in_lightgroup(self.lightgroup)
        for obj in fit_list:
            if obj.name != self.obj_name:
                obj.hide_viewport = True
                obj.hide_render = True
            else:
                obj.hide_viewport = False
                obj.hide_render = False

        return {'FINISHED'}

# reset all solo with light group
class VIEW_OT_reset_solo_lightgroup(bpy.types.Operator):
    bl_idname = "view.reset_solo_lightgroup"
    bl_label = "Reset Solo"
    bl_option = {'INTERNAL', 'UNDO'}

    def execute(self, context):
        # get all lightgroup objects
        from .ui import get_obj_list_in_lightgroup
        for lightgroup_item in context.view_layer.lightgroups:
            obj_list = get_obj_list_in_lightgroup(lightgroup_item.name)
            for obj in obj_list:
                obj.hide_viewport = False
                obj.hide_render = False


        return {'FINISHED'}


def register():
    bpy.utils.register_class(VIEW_OT_set_active_obj)
    bpy.utils.register_class(VIEW_OT_select_obj_by_lightgroup)
    bpy.utils.register_class(VIEW_OT_toggle_lightgroup_visibility)
    bpy.utils.register_class(VIEW_OT_solo_lightgroup_object)
    bpy.utils.register_class(VIEW_OT_solo_light_in_lightgroup)
    bpy.utils.register_class(VIEW_OT_reset_solo_lightgroup)


def unregister():
    bpy.utils.unregister_class(VIEW_OT_set_active_obj)
    bpy.utils.unregister_class(VIEW_OT_select_obj_by_lightgroup)
    bpy.utils.unregister_class(VIEW_OT_toggle_lightgroup_visibility)
    bpy.utils.unregister_class(VIEW_OT_solo_lightgroup_object)
    bpy.utils.unregister_class(VIEW_OT_solo_light_in_lightgroup)
    bpy.utils.unregister_class(VIEW_OT_reset_solo_lightgroup)
