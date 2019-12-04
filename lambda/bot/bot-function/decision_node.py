class decision_node() :
    prompt = ""
    fallback_prompt = ""
    slot_name = ""
    trigger_action = []
    terminal_node = False
    response_nodes = None
    actionMetadata = None
        
    def __init__(self,prompt,fallback_prompt,response_nodes,trigger_action,slot_name,actionMetadata,terminal_node=False):
        self.prompt = prompt
        self.fallback_prompt = fallback_prompt
        self.response_nodes = response_nodes
        self.trigger_action = trigger_action
        self.actionMetadata = actionMetadata
        self.slot_name = slot_name
        if response_nodes is None :
            self.terminal_node = True
    
    def get_prompt(self):
        return self.prompt
    
    def get_slot_name(self):
        return self.slot_name
    
    def get_fallback_prompt(self):
        return self.fallback_prompt
    
    def get_next_node(self,response):
        return self.response_nodes.get(response,None)
    
    def get_trigger_action(self):
        return self.trigger_action
    
    def get_action_metadata(self):
        return self.actionMetadata
        
    def is_terminal_node(self) :
        return self.terminal_node