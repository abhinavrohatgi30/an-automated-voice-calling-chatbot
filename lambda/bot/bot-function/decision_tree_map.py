import yaml
from decision_tree import decision_tree

class decision_tree_map() :
    d_tree_map = {}
    filePath = ""
    
    def __init__(self,filePath):
        self.filePath = filePath
        if filePath is not None:
            with open(filePath, 'r') as content_file:
                content = content_file.read()
            y = yaml.safe_load(content)
            for intent in y['intents']:
                intentName = intent['intentName']
                intentFlow = intent['intentFlow']
                d_tree = decision_tree(intentFlow)
                self.d_tree_map[intentName] = d_tree
                
    def get_decision_tree_map(self):
        return self.d_tree_map