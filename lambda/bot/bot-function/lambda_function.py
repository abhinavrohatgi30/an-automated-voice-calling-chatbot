import json
import boto3
import re
from actions import ActionFactory
from actions import Action
from utils import Utils
from decision_node import decision_node
from decision_tree import decision_tree
from decision_tree_map import decision_tree_map
from bot_init import BotInitialize

dynamodb = boto3.client('dynamodb')
d_tree_map_by_file_name = {}
actionFactory = ActionFactory()


def get_decision_node(root,path):
    d2 = Utils().get_decision_node(root,path,0)
    return d2
    
def update_call_status(callId, callStatus):
    keyRequest = {"callId": {'N': str(callId)}}
    updateExpression = "SET callStatus=:statusValue"
    expressionAttributes = {':statusValue': {'S' : callStatus}}
    dynamodb.update_item(TableName='callTriggerTable', Key=keyRequest, ExpressionAttributeValues=expressionAttributes, UpdateExpression=updateExpression)


def retrieve_next_prompt(decision_node,data,lastPromptStatus):
    prompt = decision_node.get_prompt()
    
    if lastPromptStatus == "ASKED":
        prompt = decision_node.get_fallback_prompt()
        
    return Utils().resolvePromptVariables(prompt,data)

def execute_action(decision_node,data,sessionAttributes):
    actions = decision_node.get_trigger_action()
    if actions is not None:
        for action in actions:
            print(action)
            actionMetadata = decision_node.get_action_metadata()
            if action is not None:
                actionFactory.getActionImpl(action).process(data,dynamodb,actionMetadata,sessionAttributes)
        
def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message, response_card):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message,
            'responseCard': response_card
        }
    }

def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }

    return response
    
def extract_session_attribute_as_slot(slots, sessionAttributes, slotName, sessionAttributesName):
    slotValue = slots[slotName]
    
    if slotValue is None:
        slotValue = sessionAttributes.get(sessionAttributesName,None)
    
    sessionAttributes[sessionAttributesName] = slotValue
    slots[slotName] = slotValue
            
    return slotValue
    
def lambda_handler(event, context):
    userId = event['userId']
    source = event['invocationSource']
    slots = event['currentIntent']['slots']   
    output_session_attributes = event['sessionAttributes'] if event['sessionAttributes'] is not None else {}
    intent_name = event['currentIntent']['name']
    
    output_session_attributes['userId'] = userId
    
    pathJson = output_session_attributes.get("path",None)
    dataJson = output_session_attributes.get("data",None)
    
    lastPromptStatus = output_session_attributes.get("lastPromptStatus",None)
    
    
    callId = extract_session_attribute_as_slot(slots,output_session_attributes,"CallId","callId")
    chatbotFlowName = extract_session_attribute_as_slot(slots,output_session_attributes,"ChatbotFlowName","chatbotFlowName")
    chatbotType = extract_session_attribute_as_slot(slots,output_session_attributes,"ChatbotType","chatbotType")
    
    
    if callId is None:
        return elicit_slot(
                        output_session_attributes,
                        intent_name,
                        slots,
                        "CallId",
                        {'contentType': 'SSML', 'content': "<speak>{}</speak>".format("Please provide a valid call Id")},
                        None
                        )
    
    if chatbotFlowName is None:
        return elicit_slot(
                        output_session_attributes,
                        intent_name,
                        slots,
                        "ChatbotFlowName",
                        {'contentType': 'SSML', 'content': "<speak>{}</speak>".format("Please provide a chatbot flow")},
                        None
                        )
    
    if chatbotType is None:
        return elicit_slot(
                        output_session_attributes,
                        intent_name,
                        slots,
                        "ChatbotType",
                        {'contentType': 'SSML', 'content': "<speak>{}</speak>".format("Please provide a chatbot type")},
                        None
                        )
    
    d_tree_map = {}
    
    print(chatbotFlowName)
    chatbot_file_name = "{}.yml".format(chatbotFlowName)
    if not chatbot_file_name in d_tree_map_by_file_name:
        d_tree_map = decision_tree_map(chatbot_file_name)
        d_tree_map_by_file_name[chatbot_file_name] = d_tree_map
    else:
        d_tree_map = d_tree_map_by_file_name.get(chatbot_file_name)
    
    print(d_tree_map_by_file_name)
    data = {}
    if dataJson is not None:
        data = json.loads(dataJson)
    else:
        data = BotInitialize(dynamodb).init(callId,chatbotType)
    
    
    
    print(json.dumps(d_tree_map.get_decision_tree_map(), default=lambda o : o.__dict__))
    d_tree = d_tree_map.get_decision_tree_map().get(intent_name)
    print(json.dumps(d_tree, default=lambda o : o.__dict__))
    root = d_tree.get_root_node()
    
    path = []
    if pathJson is not None :
        path = json.loads(pathJson)
    
    
    #Respond straightaway if the root node is a terminal node.
    if root.is_terminal_node() :
        update_call_status(callId,"Call Answered")
        execute_action(root,data,output_session_attributes)
        prompt = retrieve_next_prompt(root,data,lastPromptStatus)
        return close(
                    output_session_attributes,
                    'Fulfilled',
                    {'contentType': 'SSML', 'content': "<speak>{}</speak>".format(prompt)}
                    )
                    
    current_decision_node = get_decision_node(root,path)
    current_slot = current_decision_node.get_slot_name()
    current_slot_value = slots[current_slot]
    next_decision_node = current_decision_node.get_next_node(current_slot_value)
    
    
    #Prompt the question for the root node.
    if len(path) == 0 and current_slot_value is None :
        update_call_status(callId,"Call Answered")
        execute_action(root,data,output_session_attributes)
        prompt = retrieve_next_prompt(root,data,lastPromptStatus)
        lastPromptStatus = "ASKED"
        output_session_attributes['lastPromptStatus'] = lastPromptStatus
        return elicit_slot(
                        output_session_attributes,
                        intent_name,
                        slots,
                        current_slot,
                        {'contentType': 'SSML', 'content': "<speak>{}</speak>".format(prompt)},
                        None
                        )
    
    
        
    print(current_slot_value)
    print(data)
    print(path)
    
    
    #Get next prompt based on user's response.
    if next_decision_node is not None:
        next_slot = next_decision_node.get_slot_name()
        lastPromptStatus = "DEFAULT"
        prompt = retrieve_next_prompt(next_decision_node,data,lastPromptStatus)
        output_session_attributes['lastPromptStatus'] = lastPromptStatus
        path.append(current_slot_value)
        output_session_attributes['path'] = json.dumps(path)
        execute_action(next_decision_node,data,output_session_attributes)
        if not next_decision_node.is_terminal_node():
            return elicit_slot(
                        output_session_attributes,
                        intent_name,
                        slots,
                        next_slot,
                        {'contentType': 'SSML', 'content': "<speak>{}</speak>".format(prompt)},
                        None
                        )
        return close(
                    output_session_attributes,
                    'Fulfilled',
                    {'contentType': 'SSML', 'content': "<speak>{}</speak>".format(prompt)}
                    )
    
    #Get fallback prompt if the question was already asked.
    lastPromptStatus = "ASKED"
    output_session_attributes['lastPromptStatus'] = lastPromptStatus
    prompt = retrieve_next_prompt(current_decision_node,data,lastPromptStatus)
    return elicit_slot(
                        output_session_attributes,
                        intent_name,
                        slots,
                        current_slot,
                        {'contentType': 'SSML', 'content': "<speak>{}</speak>".format(prompt)},
                        None
                        )
    
        
