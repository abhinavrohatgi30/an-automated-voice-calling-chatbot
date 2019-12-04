class BotInitialize():
    
    dynamodb = None
    
    def __init__(self,dynamodb):
        self.dynamodb = dynamodb
    
    def init(self,callId,chatbot_type) :
        data = {}
        
        call_details = self.fetch_call_details(callId)
        if chatbot_type == "JOBSEEKER":
            candidateId = call_details['candidateId']
            candidate = self.fetch_candidate_details_by_cand_id(candidateId)
            data['candidateName'] = candidate['candidateName']
            data['candidateId'] = candidateId
            data['candidateCTC'] = candidate['ctc']
            data['candidatePhoneNumber'] = candidate['phoneNumber']
            data['candidateLocation'] = candidate['location']
        elif chatbot_type == "JOB_RECOMMENDATION" :
            jobId = call_details['jobId']
            candidateId = call_details['candidateId']
            recommendation = self.fetch_job_details_by_job_id(jobId)
            candidate = self.fetch_candidate_details_by_cand_id(candidateId)
            data['candidateName'] = candidate['candidateName']
            data['candidateId'] = candidateId
            data['candidateCTC'] = candidate['ctc']
            data['candidatePhoneNumber'] = candidate['phoneNumber']
            data['candidateLocation'] = candidate['location']
            data['jobCompanyName'] = recommendation['companyName']
            data['jobLocation'] = recommendation['location']
            data['jobMinExperience'] = recommendation['minExperience']
            data['jobMaxExperience'] = recommendation['maxExperience']
            data['jobMinCTC'] = recommendation['minCTC']
            data['jobMaxCTC'] = recommendation['maxCTC']
            data['jobTitle'] = recommendation['jobName']
            data['jobId'] = recommendation['jobId']
            data['slot1Time'] = recommendation.get('slot1Time','')
            data['slot2Time'] = recommendation.get('slot2Time','')
            data['slot3Time'] = recommendation.get('slot3Time','')
        return data
        
    
    def fetch_call_details(self,callId):
        response = self.dynamodb.get_item(TableName='callTriggerTable', Key={'callId':{'N':callId}})
            
        candidateId = str(response['Item']['candidateId']['S'])
        jobId = None
        if 'jobId' in response['Item']: 
            jobId = str(response['Item']['jobId']['S'])
        
        return {'candidateId':candidateId,"jobId":jobId}
    
        
        
    def fetch_candidate_details_by_cand_id(self,candidateId):
        response = self.dynamodb.get_item(TableName='jobseekers', Key={'candidateId':{'N':candidateId}},
            AttributesToGet=['candidateName','location','ctc','phoneNumber'])
            
        candidateName = response['Item']['candidateName']['S']
        location = response['Item']['location']['S']
        ctc = response['Item']['ctc']['S']
        phoneNumber = response['Item']['phoneNumber']['S']
        
        return {'candidateId':candidateId,'candidateName':candidateName,'location':location,'ctc':ctc,'phoneNumber':phoneNumber}
        
    
    def fetch_job_details_by_job_id(self,jobId):
        job = {}
        job_response = self.dynamodb.get_item(TableName='jobs', Key={'jobId':{'N':jobId}})
        job['jobId'] = jobId
        job['jobName'] = job_response['Item']['jobName']['S']
        job['companyName'] = job_response['Item']['companyName']['S']
        job['maxCTC'] = job_response['Item']['maxCTC']['N']
        job['minCTC'] = job_response['Item']['minCTC']['N']
        job['maxExperience'] = job_response['Item']['maxExperience']['N']
        job['minExperience'] = job_response['Item']['minExperience']['N']
        job['location'] = job_response['Item']['location']['S']
        job['slot1Time'] = job_response['Item'].get('slot1Time',{"S":""})['S']
        job['slot2Time'] = job_response['Item'].get('slot2Time',{"S":""})['S']
        job['slot3Time'] = job_response['Item'].get('slot3Time',{"S":""})['S']
        
        return job
    
    def fetch_recommendation_by_cand_id(self,candidateId):
        payload1 = {
            "TableName" : "recommendations",
            "FilterExpression" : "candidateId = :candidateId",
            "ExpressionAttributeValues" : { ":candidateId" :{"N":str(candidateId)}}
            }
        dynamo_response = self.dynamodb.scan(**payload1)
        jobs = []
        jobIds = []
        for item in dynamo_response['Items']:
            jobId = item['jobId']['N']
            job_response = fetch_job_details_by_job_id(jobId)
            job = {}
            job['jobId'] = jobId
            job['jobName'] = job_response['Item']['jobName']['S']
            job['companyName'] = job_response['Item']['companyName']['S']
            job['maxCTC'] = job_response['Item']['maxCTC']['N']
            job['minCTC'] = job_response['Item']['minCTC']['N']
            job['maxExperience'] = job_response['Item']['maxExperience']['N']
            job['minExperience'] = job_response['Item']['minExperience']['N']
            job['location'] = job_response['Item']['location']['S']
            job['skill1'] = job_response['Item']['skill1']['S']
            job['skill2'] = job_response['Item']['skill2']['S']
            job['skill3'] = job_response['Item']['skill3']['S']
            job['slot1Time'] = job_response['Item'].get('slot1Time',{"S":""})['S']
            job['slot2Time'] = job_response['Item'].get('slot2Time',{"S":""})['S']
            job['slot3Time'] = job_response['Item'].get('slot3Time',{"S":""})['S']
            jobs.append(job)
        return jobs
