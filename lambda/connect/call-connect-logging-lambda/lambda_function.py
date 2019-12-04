import json
import boto3

dynamodb = boto3.client('dynamodb')

def lambda_handler(event, context):
    event_json = json.dumps(event)
    print("Event JSON  {}".format(event))
    phoneNumber = event['Details']['ContactData']['CustomerEndpoint']['Address']
    callId = event['Details']['ContactData']['Attributes']['callId']
    candidateId = event['Details']['ContactData']['Attributes']['candidateId']
    chatbotFlowName = event['Details']['ContactData']['Attributes']['chatbotFlowName']
    keyRequest = {"callId": {'N': str(callId)}}
    updateExpression = "SET callStatus=:statusValue"
    response = {
        "candidateId" : {"N" : str(candidateId)},
        "chatbotFlowName" : {"S" : chatbotFlowName},
        "status" : {"S" : "CALL_PICKED"},
        "callId" : {"S": str(callId)}
    }
    expressionAttributes = {':statusValue': {'S' : 'Call Picked'}}
    dynamodb.update_item(TableName='callTriggerTable', Key=keyRequest, ExpressionAttributeValues=expressionAttributes, UpdateExpression=updateExpression)
    dynamodb.put_item(TableName='candidateResponse', Item=response)
    return {
        "statusCode" : 200
    }
