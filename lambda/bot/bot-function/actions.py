import json
import dateutil.parser
import datetime

class ActionFactory() :
    actionMap = {}
    
    def __init__(self):
        for c in Action.__subclasses__():
            self.actionMap[c.get_name()] = c
    
    def getActionImpl(self,trigger_action):
        return self.actionMap.get(trigger_action,None)
        

class Action():
    def get_name():
        pass
    
    def process(data,dynamodb,actionMetadata,sessionAttributes):
        pass
    
class TestAction1(Action):

    def get_name():
        return "saveApplyStatus"
    
    def process(data,dynamodb,actionMetadata,sessionAttributes):
        candidateId = data['candidateId']
        jobId = data['jobId']
        userId = sessionAttributes['userId']
        applicationId = "{}_{}".format(candidateId,jobId)
        createdAt = str(datetime.datetime.now());
        response = {
            "candidateId" : {"N":candidateId},
            "jobId" : {"N":jobId},
            "userId" : {"S":userId},
            "applicationId" : {"S":applicationId},
            "createdAt" : {"S":createdAt}
        }
        dynamodb.put_item(TableName='jobApplications', Item=response)

class TestAction2(Action):   

    def get_name():
        return "saveQuestionaireAnswers"
        
    def process(data,dynamodb,actionMetadata,sessionAttributes):
        candidateId = data['candidateId']
        jobId = data['jobId']
        path = json.loads(sessionAttributes['path'])
        ctcHikeAnswer = path[-1]
        locationAnswer = path[-2]
        interviewStatusAnswer = path[-3]
        ctcHike = False
        locationProximity = False
        interviewStatus = False
        if ctcHikeAnswer == "yes":
            ctcHike = True
        if locationAnswer == "yes":
            locationProximity = True
        if interviewStatusAnswer == "yes":
            interviewStatus = True
        userId = sessionAttributes['userId']
        skillExperienceId = "{}_{}".format(candidateId,jobId)
        createdAt = str(datetime.datetime.now());
        response = {
            "candidateId" : {"N":candidateId},
            "jobId" : {"N":jobId},
            "userId" : {"S":userId},
            "skillExperienceId" : {"S": skillExperienceId},
            "locationProximity" : {"BOOL": locationProximity},
            "ctcHike" : {"BOOL": ctcHike},
            "interviewStatus" : {"BOOL": interviewStatus},
            "createdAt" : {"S":createdAt}
        }
        dynamodb.put_item(TableName='skillExperienceTable', Item=response)
    
    def resolveAnswer(answer):
        if answer == "yes":
            return True
        elif answer == "no":
            return False

class TestAction3(Action):   

    def get_name():
        return "saveRejectStatus"
    
    def process(data,dynamodb,actionMetadata,sessionAttributes):
        candidateId = data['candidateId']
        jobId = data['jobId']
        userId = sessionAttributes['userId']
        rejectionId = "{}_{}".format(candidateId,jobId)
        createdAt = str(datetime.datetime.now());
        response = {
            "candidateId" : {"N":candidateId},
            "jobId" : {"N":jobId},
            "userId" : {"S":userId},
            "rejectionId" : {"S":rejectionId},
            "createdAt" : {"S":createdAt}
        }
        dynamodb.put_item(TableName='jobRejections', Item=response)

class TestAction4(Action):
    
    def get_name():
        return "saveNotInterested"
    
    def process(data,dynamodb,actionMetadata,sessionAttributes):
        candidateId = data['candidateId']
        userId = sessionAttributes['userId']
        phoneNumber = data['candidatePhoneNumber']
        createdAt = str(datetime.datetime.now());
        response = {
            "candidateId" : {"N":candidateId},
            "userId" : {"S":userId},
            "createdAt" : {"S":createdAt},
            "phoneNumber" : {"S":phoneNumber}
        }
        dynamodb.put_item(TableName='notInterestedCandidates', Item=response)
        
class TestAction5(Action):  

    def get_name():
        return "saveNeedSupportStatus"
    
    def process(data,dynamodb,actionMetadata,sessionAttributes):
        print("Test Action 5")

class TestAction6(Action): 

    def get_name():
        return "saveInterested"
    
    def process(data,dynamodb,actionMetadata,sessionAttributes):
        print("TestAction6")


class TestAction7(Action): 

    def get_name():
        return "saveStatus"
    
    def process(data,dynamodb,actionMetadata,sessionAttributes):
        data.update(sessionAttributes)
        response = {
        "candidateId" : {"N" : data['candidateId']},
        "chatbotFlowName" : {"S" : data['chatbotFlowName']},
        "status" : {"S" : actionMetadata['status']},
        "data" : {"S" : json.dumps(data)},
        "callId" : {"S": sessionAttributes['callId']}
        }
        print(actionMetadata['status'])
        dynamodb.put_item(TableName='candidateResponse', Item=response)