from rest_framework import serializers

from job.models import JobConfiguration,Job,JobCustom


GET_JOB = """
- Method to list down details of all the job.
Note:
- to perform dynamic filter pass the field and its value in the request
- Request samples:
        - http://dev-awsnlb.simplifyvms.com:8002/job-manager/0ea71e62-6d04-4aac-8067-b55a56cfaa5a/job?type=development
- Header samples:
        - Content-Type: application/json

- Need to provide primary key in the request url to get the record specific to
  that primary key.
- Request samples:
        - http://dev-awsnlb.simplifyvms.com:8002/job-manager/0ea71e62-6d04-4aac-8067-b55a56cfaa5a/job/3435d259-a742-4bc7-b002-8c52c92b893c

- Header samples:
        - X-SVMS-Program-Id:  <program_id>  (optional)        
"""

POST_JOB = """ 
- Add a job with program id. 
- below are the sample request url and body 

- Request samples:
        - http://dev-awsnlb.simplifyvms.com:8002/job-manager/19106c90-e1f5-4016-b7bf-3cdf24a2b185/job
        - body
            {
             "category": "1",
             "title": 1,
            }
Note:
This method create the custom column with the
        mapping column data
        for e.g - 
        {"column_1":"Python Developer"}   # Job Model
        {"column_1":"Job Title"}   # column mapping
"""

PUT_JOB = """
- This method allows to update job entry with the help
  of primary key provided in the requested url.
Note:
This method modified the custom column names with the
        mapping column data
        for e.g - 
        {"column_1":"Python Developer"}   # Job Model
        {"column_1":"Job Title"}   # column mapping
        Output :
        {"Job title":"Python Developer"}

- Request samples:
        - http://dev-awsnlb.simplifyvms.com:8002/job-manager/0ea71e62-6d04-4aac-8067-b55a56cfaa5a/job/3435d259-a742-4bc7-b002-8c52c92b893c

"""

DELETE_JOB = """ 
- Method helps to delete(soft delete) a job record 
  with the help of the primary key provided in the requested url.
- Request samples:
        - http://dev-awsnlb.simplifyvms.com:8002/job-manager/0ea71e62-6d04-4aac-8067-b55a56cfaa5a/job/3435d259-a742-4bc7-b002-8c52c92b893c
- Header samples:
        - Content-Type: application/json
"""

POST_JOB_CONFIGRATION = """ 
-Create system defined & custom fields Json configurator and insert column values in table. 

"""


POST_COPYJOB = """
- Copy job with program id. 
- below are the sample request url
- Request samples:
        - http://dev-awsnlb.simplifyvms.com:8002/job-manager/19106c90-e1f5-4016-b7bf-3cdf24a2b185/copyjob
        
"""


PUT_JobApproval = """
- This method allows to update job entry with the help
  of primary key provided in the requested url.

- Request samples:
        - http://dev-awsnlb.simplifyvms.com:8002/job-manager/0ea71e62-6d04-4aac-8067-b55a56cfaa5a/job_approval/3435d259-a742-4bc7-b002-8c52c92b893c

"""


GET_RECENTJOB = """
- Method to list down details of all the recentjob.
Note:
- Request samples:
        - http://dev-awsnlb.simplifyvms.com:8002/job-manager/0ea71e62-6d04-4aac-8067-b55a56cfaa5a/recent_job
- Header samples:
        - Content-Type: application/json

- Need to provide primary key in the request url to get the record specific to
  that primary key.
- Request samples:
        - http://dev-awsnlb.simplifyvms.com:8002/job-manager/0ea71e62-6d04-4aac-8067-b55a56cfaa5a/recent_job/3435d259-a742-4bc7-b002-8c52c92b893c
     
"""

GET_DRAFTJOB = """
- Method to list down details of all the draftjob.
Note:
- Request samples:
        - http://dev-awsnlb.simplifyvms.com:8002/job-manager/0ea71e62-6d04-4aac-8067-b55a56cfaa5a/draft_job
- Header samples:
        - Content-Type: application/json

- Need to provide primary key in the request url to get the record specific to
  that primary key.
- Request samples:
        - http://dev-awsnlb.simplifyvms.com:8002/job-manager/0ea71e62-6d04-4aac-8067-b55a56cfaa5a/draft_job/3435d259-a742-4bc7-b002-8c52c92b893c
     
"""
GET_POPULARJOB = """
- Method to list down details of all the popularjob.
Note:
- Request samples:
        - http://dev-awsnlb.simplifyvms.com:8002/job-manager/0ea71e62-6d04-4aac-8067-b55a56cfaa5a/popular_job
- Header samples:
        - Content-Type: application/json

- Need to provide primary key in the request url to get the record specific to
  that primary key.
- Request samples:
        - http://dev-awsnlb.simplifyvms.com:8002/job-manager/0ea71e62-6d04-4aac-8067-b55a56cfaa5a/popular_job/3435d259-a742-4bc7-b002-8c52c92b893c
     
"""
GET_JOBTEMPLATE = """
- Method to list down details of all the jobtemplate.
Note:
- Request samples:
        - http://dev-awsnlb.simplifyvms.com:8002/job-manager/0ea71e62-6d04-4aac-8067-b55a56cfaa5a/job_template
- Header samples:
        - Content-Type: application/json

- Need to provide primary key in the request url to get the record specific to
  that primary key.
- Request samples:
        - http://dev-awsnlb.simplifyvms.com:8002/job-manager/0ea71e62-6d04-4aac-8067-b55a56cfaa5a/job_template/3435d259-a742-4bc7-b002-8c52c92b893c
     
"""
GET_JOBQUALIFICATION = """
- Method to list down details of all the jobtemplate.
Note:
- Need to provide primary key in the request url to get the record specific to
  that primary key.
- Request samples:
        - http://dev-awsnlb.simplifyvms.com:8002/job-manager/0ea71e62-6d04-4aac-8067-b55a56cfaa5a/job/qualification/3435d259-a742-4bc7-b002-8c52c92b893c
- Header samples:
        - Content-Type: application/json
"""

GET_UNIQUETEMPLATE = """
- Method to list down details of uniquetemplate.
Note:
- Need to provide primary key in the request url to get the record.
- Request samples:
        - http://dev-awsnlb.simplifyvms.com:8002/job-manager/0ea71e62-6d04-4aac-8067-b55a56cfaa5a/unique_template_name
- Header samples:
        - Content-Type: application/json
"""
