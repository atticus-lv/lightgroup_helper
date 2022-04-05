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


def register():
    bpy.utils.register_class(VIEW_OT_set_active_obj)
    bpy.utils.register_class(VIEW_OT_select_obj_by_lightgroup)

def unregister():
    bpy.utils.unregister_class(VIEW_OT_set_active_obj)
    bpy.utils.unregister_class(VIEW_OT_select_obj_by_lightgroup)