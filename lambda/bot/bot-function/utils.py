from decision_node import decision_node

class Utils() : 
    
    def create_root_node(self,config,node_name):
        node = config[node_name]
        prompt = node['prompt']
        triggerAction = node.get('triggerAction',None)
        actionMetadata = node.get('actionMetadata',None)
        failurePrompt = node.get('failurePrompt',None)
        slotName = node.get('slotName',None)
        response_nodes = {}
        if 'response_nodes' in node :
            response_nodes_config = node['response_nodes']
            keys = response_nodes_config.keys()
            for key in keys:
                node_name = response_nodes_config[key]
                response_nodes[key] = self.create_root_node(config,node_name)
            return decision_node(prompt,failurePrompt,response_nodes,triggerAction,slotName,actionMetadata)
        else:
            return decision_node(prompt,failurePrompt,None,triggerAction,slotName,actionMetadata)
    
    def resolvePromptVariables(self,prompt,data):
        for key in data.keys():
            prompt = prompt.replace(":{}".format(key),str(data[key]))
        return prompt

    def get_decision_node(self,root_node,traversal_path, traversed_count):
        if len(traversal_path) > traversed_count:
            return self.get_decision_node(root_node.get_next_node(traversal_path[traversed_count]),traversal_path,traversed_count+1)
        else:
            return root_node