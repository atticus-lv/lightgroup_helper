import bpy


def redraw_area():
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            area.tag_redraw()


class LGH_OT_set_light_group(bpy.types.Operator):
    bl_idname = 'lgh.set_light_group'
    bl_label = 'Set Light Group'
    bl_option = {'UNDO_GROUPED'}

    dep_classes = []

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 0 and context.object is not None

    def execute(self, context):
        self.dep_classes.clear()

        # create_new_light_group
        def create_new_light_group(self, context):
            bpy.ops.scene.view_layer_add_lightgroup()
            target_lightgroup = context.view_layer.lightgroups[-1].name

            for obj in context.selected_objects:
                obj.lightgroup = target_lightgroup
            return {'FINISHED'}

        op_create_new_light_group = type("DynOp",
                                         (bpy.types.Operator,),
                                         {"bl_idname": f'lgh.set_light_group_new',
                                          "bl_label": "New Light Group",
                                          "bl_description": f"Set Selected Objects' light group to a new light group ",
                                          "execute": create_new_light_group,
                                          })
        self.dep_classes.append(op_create_new_light_group)

        # existing light groups
        for index, lightgroup_item in enumerate(context.view_layer.lightgroups):

            def execute(self, context):
                for obj in context.selected_objects:
                    obj.lightgroup = self.target_lightgroup

                redraw_area()
                return {'FINISHED'}

            op_cls = type("DynOp",
                          (bpy.types.Operator,),
                          {"bl_idname": f'lgh.set_light_group_{index}',
                           "bl_label": lightgroup_item.name,
                           "bl_description": f"Set Selected Objects' light group to '{lightgroup_item.name}'",
                           "execute": execute,
                           # custom pass in
                           'target_lightgroup': lightgroup_item.name,
                           },
                          )

            self.dep_classes.append(op_cls)

        # register
        for cls in self.dep_classes:
            bpy.utils.register_class(cls)

        dep_classes = self.dep_classes

        if len(context.view_layer.lightgroups) == 0:
            create_new_light_group(self, context)
            return {'FINISHED'}
        else:

            def draw_all_coll(self, context):
                layout = self.layout
                for cls in dep_classes:
                    if cls.bl_idname == 'lgh.set_light_group_new':
                        layout.operator(cls.bl_idname, icon='ADD')
                        layout.separator()
                    else:
                        layout.operator(cls.bl_idname, icon='LIGHT')

            context.window_manager.popup_menu(draw_all_coll, title="Set Light Group")
            redraw_area()

        return {'FINISHED'}


def register():
    bpy.utils.register_class(LGH_OT_set_light_group)


def unregister():
    bpy.utils.unregister_class(LGH_OT_set_light_group)
