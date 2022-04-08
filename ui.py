import bpy


def get_visible_collections():
    def check_child(child, vis_cols):
        if child.is_visible:
            vis_cols.append(child.collection)
            for sub_child in child.children:
                vis_cols = check_child(sub_child, vis_cols)
        return vis_cols

    vis_cols = [bpy.context.scene.collection]

    for child in bpy.context.window.view_layer.layer_collection.children:
        check_child(child, vis_cols)

    return vis_cols


def get_obj_list_in_lightgroup(lightgroup_name):
    view_layer = bpy.context.view_layer

    coll_list = get_visible_collections()
    obj_list = list()

    for coll in coll_list:
        for obj in coll.all_objects:
            if obj.lightgroup != view_layer.lightgroups[lightgroup_name].name: continue
            obj_list.append(obj)

    return list(set(obj_list))


class LGH_PT_Panel(bpy.types.Panel):
    bl_label = "Light Group"
    bl_region_type = 'UI'
    bl_category = "LGH"
    bl_space_type = "VIEW_3D"
    bl_option = {'DEFAULT_CLOSED'}

    def draw(self, context):
        if bpy.app.version < (3, 2, 0): return

        layout = self.layout

        view_layer = context.view_layer

        row = layout.row()
        col = row.column()
        col.template_list("UI_UL_list", "lightgroups", view_layer,
                          "lightgroups", view_layer, "active_lightgroup_index", rows=2)

        col = row.column()
        sub = col.column(align=True)
        sub.operator("scene.view_layer_add_lightgroup", icon='ADD', text="")
        sub.operator("scene.view_layer_remove_lightgroup", icon='REMOVE', text="")

        if len(view_layer.lightgroups) == 0: return


class LGH_PT_ObjectPanel(bpy.types.Panel):
    bl_label = "Object"
    bl_region_type = "UI"
    bl_category = "LGH"
    bl_space_type = "VIEW_3D"

    def draw(self, context):
        ob = context.object
        view_layer = context.view_layer

        if ob is None and not hasattr(ob, 'lightgroup'): return
        layout = self.layout
        col = layout.column(align=True)
        col.use_property_split = True
        col.use_property_decorate = False

        col.prop(ob, 'name', icon="OBJECT_DATA" if ob.type != 'LIGHT' else "LIGHT")
        col.prop_search(ob, "lightgroup", view_layer, "lightgroups", text="Light Group")

        col = layout.box().column(align=True)
        col.use_property_split = True
        col.use_property_decorate = False

        col.label(text='Visibility')
        row = col.row(align=True)
        row.scale_y = 1.15
        row.scale_x = 1.25
        row.alignment = 'CENTER'
        row.prop(ob, "hide_select", text="", )
        row.prop(ob, "hide_viewport", text="", )
        row.prop(ob, "hide_render", text="", )
        row.prop(ob, "is_holdout", text="", icon='HOLDOUT_ON')
        row.prop(ob, "is_shadow_catcher", text="", icon='GHOST_ENABLED')

        col.separator()

        col.label(text='Ray Visibility')
        row = col.row(align=True)
        row.scale_y = 1.15
        row.scale_x = 1.25
        row.alignment = 'CENTER'
        row.prop(ob, "visible_camera", text="", icon='CAMERA_DATA')
        row.prop(ob, "visible_diffuse", text="", icon='SHADING_SOLID')
        row.prop(ob, "visible_glossy", text="", icon='NODE_MATERIAL')
        row.prop(ob, "visible_transmission", text="", icon='MATERIAL')
        row.prop(ob, "visible_volume_scatter", text="", icon='VOLUME_DATA')

        col.separator()

        col.label(text='Viewport Display')
        row = col.row(align=True)
        row.scale_y = 1.15
        row.scale_x = 1.25
        row.alignment = 'CENTER'
        row.prop(ob, "show_name", icon='EVENT_N', text='')
        row.prop(ob, "show_axis", icon='EMPTY_AXIS', text='')
        row.prop(ob, "show_wire", icon='MOD_WIREFRAME', text='')
        row.prop(ob, "show_in_front", icon='AXIS_FRONT', text='')
        row = col.row(align=True)
        row.scale_y = 1.15
        row.scale_x = 1.25
        row.alignment = 'CENTER'
        row.prop(ob, "display_type")


class LGH_PT_ToolPanel(bpy.types.Panel):
    bl_label = "Tool"
    bl_region_type = "UI"
    bl_category = "LGH"
    bl_space_type = "VIEW_3D"

    def draw(self, context, ):
        layout = self.layout
        layout.scale_y = 1.2
        row = layout.row(align=True)
        row.alignment = 'CENTER'
        row.operator('lgh.set_light_group')
        row.separator()
        row.operator('view.reset_solo_lightgroup')

        self.draw_all_lightgroups(context, layout)

    def draw_single_lightgroup(self, view_layer, obj, layout):
        row = layout.row(align=True)
        # solo light in light group
        solo = row.operator('view.solo_light_in_lightgroup', text='', icon='EVENT_S')
        solo.lightgroup = obj.lightgroup
        solo.obj_name = obj.name
        row.separator()
        # select objects
        row.operator('view.set_active_obj', icon="OBJECT_DATA" if obj.type != 'LIGHT' else "LIGHT",
                     text=obj.name).obj_name = obj.name
        row.separator()
        # object property
        row.prop(obj, 'hide_viewport', text='')
        row.prop(obj, 'hide_render', text='')

    def draw_all_lightgroups(self, context, layout):

        for lightgroup_item in context.view_layer.lightgroups:
            fit_list = get_obj_list_in_lightgroup(lightgroup_item.name)
            col = layout.box().column(align=True)
            col.use_property_split = True
            col.use_property_decorate = False

            row = col.row(align=True)
            row.scale_x = 1.15
            row.operator('view.solo_lightgroup_object', text='', icon='EVENT_S').lightgroup = lightgroup_item.name
            row.separator(factor=1)
            row.operator('lgh.rename_light_group', text=lightgroup_item.name).lightgroup_name = lightgroup_item.name

            row.separator(factor=2)

            row.operator('view.toggle_lightgroup_visibility', icon='HIDE_OFF',
                         text='').lightgroup = lightgroup_item.name
            row.operator('view.select_obj_by_lightgroup', text='',
                         icon="RESTRICT_SELECT_OFF").lightgroup = lightgroup_item.name

            row.separator(factor=2)
            row.operator('lgh.remove_light_group',icon = 'X',text = '').lightgroup_name = lightgroup_item.name

            col.separator()

            if len(fit_list) == 0: col.label(text='Nothing in this Light Group')

            for obj in fit_list:
                self.draw_single_lightgroup(context.view_layer, obj, col)


def register():
    bpy.utils.register_class(LGH_PT_Panel)
    bpy.utils.register_class(LGH_PT_ObjectPanel)
    bpy.utils.register_class(LGH_PT_ToolPanel)


def unregister():
    bpy.utils.unregister_class(LGH_PT_Panel)
    bpy.utils.unregister_class(LGH_PT_ObjectPanel)
    bpy.utils.unregister_class(LGH_PT_ToolPanel)
