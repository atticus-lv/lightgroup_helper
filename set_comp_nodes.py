import bpy


# generate composite nodes for viewlayer lightgroup
class NODE_OT_set_lightgroup_postprocess_nodes(bpy.types.Operator):
    bl_idname = "node.set_lightgroup_postprocess_nodes"
    bl_label = "Set Lightgroup Postprocess Nodes"

    @classmethod
    def poll(cls, context):
        return (context.scene.use_nodes and
                context.scene.render.engine == 'CYCLES' and
                context.scene.node_tree.nodes.active.bl_idname == 'CompositorNodeRLayers')

    def execute(self, context):
        # get viewlayer node in composite node tree
        nt = context.scene.node_tree
        viewlayer_node = nt.nodes.active
        viewlayer_name = viewlayer_node.layer

        # new nodes

        # get lightgroup passes in viewlayer node
        lg_list = [lightgroup_item.name for lightgroup_item in context.scene.view_layers[viewlayer_name].lightgroups]
        lg_passes = ['Combined_' + lightgroup_name for lightgroup_name in lg_list]

        # when there is no lightgroup
        if len(lg_list) == 0 or len(lg_list) == 1:
            return {'CANCELLED'}

        # create group node
        group_node = nt.nodes.new('CompositorNodeGroup')
        group_node.location = (viewlayer_node.location[0] + 300, viewlayer_node.location[1])
        group_nt = bpy.data.node_groups.new(name='LG_' + viewlayer_name, type='CompositorNodeTree')
        group_node.node_tree = group_nt

        # create group input node and output node
        group_input_node = group_nt.nodes.new('NodeGroupInput')
        group_output_node = group_nt.nodes.new('NodeGroupOutput')
        group_input_node.location = (0, 0)
        group_output_node.location = (500, 0)

        new_nodes = list()

        # when there is muiltiple lightgroups, we need to add lightgroup nodes with mix rgb node(ADD)
        for i in range(len(lg_list)):
            add_node = self.create_lightgroup_pass_nodes(group_nt, location=(
                viewlayer_node.location[0] + (i + 2) * 175, viewlayer_node.location[1] - (i + 1) * 100))
            new_nodes.append(add_node)

        # add add node to combine lightgroup passes
        last_add_node = None

        for i, add_node in enumerate(new_nodes):
            if last_add_node is None:
                add_node.inputs[1].default_value = (0, 0, 0, 1)  # set black color for the first node
                # add mix input
                group_nt.links.new(group_input_node.outputs[-1], add_node.inputs[0])
                group_nt.links.new(group_input_node.outputs[-1], add_node.inputs[2])
            else:
                group_nt.links.new(group_input_node.outputs[-1], add_node.inputs[0])
                group_nt.links.new(last_add_node.outputs[0], add_node.inputs[1])
                group_nt.links.new(group_input_node.outputs[-1], add_node.inputs[2])

            last_add_node = add_node
        # link to output
        group_nt.links.new(last_add_node.outputs[0], group_output_node.inputs[0])

        # link viewlayer node to group node
        for i, lg_pass in enumerate(lg_passes):
            nt.links.new(viewlayer_node.outputs[lg_pass], group_node.inputs[i * 2 + 1])

        return {'FINISHED'}

    def create_lightgroup_pass_nodes(self, nt, location=(0, 0)):
        add_node = nt.nodes.new('CompositorNodeMixRGB')
        add_node.blend_type = 'ADD'
        add_node.location = location
        add_node.use_alpha = True
        return add_node

def menu_fun(self, context):
    if context.space_data.node_tree and context.space_data.node_tree.nodes.active.bl_idname == 'CompositorNodeRLayers':
        self.layout.operator(NODE_OT_set_lightgroup_postprocess_nodes.bl_idname, text="Combine Lightgroup Passes")
        self.layout.separator()

def register():
    bpy.utils.register_class(NODE_OT_set_lightgroup_postprocess_nodes)
    # add to context menu
    bpy.types.NODE_MT_context_menu.prepend(menu_fun)


def unresister():
    bpy.utils.unregister_class(NODE_OT_set_lightgroup_postprocess_nodes)

    bpy.types.NODE_MT_context_menu.remove(menu_fun)