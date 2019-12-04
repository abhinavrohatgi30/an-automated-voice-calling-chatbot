from decision_node import decision_node
from utils import Utils

class decision_tree():
    filePath = "";
    root = decision_node("","",None,None,None,None)
    
    def __init__(self,config) :
        self.root = Utils().create_root_node(config,"root_node")
        
    def get_root_node(self):
        return self.root
    
    def get_decision_node(self,path):
        return self.root
    
    def get_prompt(self, decision_node):
        return decision_node.get_prompt()