import json
import boto3

connect = boto3.client("connect")

dynamodb = boto3.client("dynamodb")


def fetch_job_details_by_job_id(jobId):
    job = {}
    job_response = dynamodb.get_item(TableName='jobs', Key={'jobId':{'N':jobId}})
    job['jobId'] = jobId
    job['jobName'] = job_response['Item']['jobName']['S']
    job['companyName'] = job_response['Item']['companyName']['S']
    job['maxCTC'] = job_response['Item']['maxCTC']['N']
    job['minCTC'] = job_response['Item']['minCTC']['N']
    job['maxExperience'] = job_response['Item']['maxExperience']['N']
    job['minExperience'] = job_response['Item']['minExperience']['N']
    job['location'] = job_response['Item']['location']['S']
    return job


def fetch_candidate_details_by_cand_id(candidateId):
    response2 = dynamodb.get_item(TableName='jobseekers', Key={'candidateId':{'N':candidateId}},
        AttributesToGet=['candidateName','location','ctc',"phoneNumber"])
        
    candidateName = response2['Item']['candidateName']['S']
    location = response2['Item']['location']['S']
    ctc = response2['Item']['ctc']['S']
    phoneNumber = response2['Item']['phoneNumber']['S']
    
    return {'candidateId':candidateId,'candidateName':candidateName,'location':location,'ctc':ctc, 'phoneNumber':phoneNumber}

def fetch_call_details(callId):
    response = dynamodb.get_item(TableName='callTriggerTable', Key={'callId':{'N':str(callId)}})
        
    candidateId = str(response['Item']['candidateId']['S'])
    jobId = None
    if 'jobId' in response['Item']: 
        jobId = str(response['Item']['jobId']['S'])
    
    chatbotType = str(response['Item']['chatbotType']['S'])
    chatbotFlowName = str(response['Item']['chatbotFlowName']['S'])
    return {'candidateId':candidateId,"jobId":jobId,"chatbotType":chatbotType,"chatbotFlowName":chatbotFlowName}

def update_call_status(callId, callStatus):
    keyRequest = {"callId": {'N': str(callId)}}
    updateExpression = "SET callStatus=:statusValue"
    expressionAttributes = {':statusValue': {'S' : callStatus}}
    dynamodb.update_item(TableName='callTriggerTable', Key=keyRequest, ExpressionAttributeValues=expressionAttributes, UpdateExpression=updateExpression)


def lambda_handler(event, context):
    callId = event['callId']
    prompt = event['prompt']
    call_details = fetch_call_details(callId)
    candidateId = call_details['candidateId']
    jobId = call_details['jobId']
    job = {}
    if jobId is not None:
        job = fetch_job_details_by_job_id(jobId)
    candidate = fetch_candidate_details_by_cand_id(candidateId)
    
    destination_phone_number = candidate['phoneNumber']
    candidateName = candidate['candidateName']
    sourcePhoneNumber = ""
    contactFlowId = ""
    
    sourcePhoneNumber = "+14153674333"
    chatbotType=call_details['chatbotType']
    
    for key in candidate.keys():
        prompt = prompt.replace(":{}".format(key),candidate[key])
        
    print(job)    
    for key in job.keys():
        prompt = prompt.replace(":{}".format(key),job[key])    
        
    chatbotFlowName=call_details['chatbotFlowName']
    contactFlowId="46b69f3f-21f0-49cc-83b4-7dbb75c9fb7b"
    attributes = {}
    attributes['callId'] = str(callId)
    attributes['candidateId'] = str(candidateId)
    attributes['prompt'] = prompt
    attributes['chatbotType'] = chatbotType
    attributes['chatbotFlowName'] = chatbotFlowName
        
    print(sourcePhoneNumber)
    print(attributes)
    response = connect.start_outbound_voice_contact(
        DestinationPhoneNumber=destination_phone_number,
        ContactFlowId=contactFlowId,
        InstanceId="a9f863c5-f618-40ce-8f0a-02febf70311b",
        SourcePhoneNumber=sourcePhoneNumber,
        Attributes=attributes
    )
    update_call_status(callId,"Call Triggered")
    return response
