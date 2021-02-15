import requests
from django.conf import settings
from job.models import Job
import json 

def vms_dashboard(job_obj):
    try:
        job_data = job_obj[0]
        url=settings.VMS_DASHBOARD
        hiring_manager = str(job_data["job_manager"]["first_name"]+" "+job_data["job_manager"]["last_name"]) if job_data["job_manager"] else None
        created_date, publish_date = get_date(job_data["created_on"])
        data = {
            "source_job_id": job_data["id"],  
            "job_title": job_data["title"]["title"],
            "job_type": job_data["type"], 
            "job_category": str(job_data["category"]["id"]),  
            "hire_type": job_data["hire_type"], 
            "company_name": job_data["company_name"],
            "company_gl_no": None,
            "company_account_unit": None,
            "no_of_openings": str(job_data["no_of_openings"]),
            "experience_level": None,
            "job_start_date": created_date, 
            "job_end_date": created_date,  
            "job_description": str(job_data["description"]),
            "compensation_currency": job_data["currency"],
            "compensation_rate": None,
            "shift_start_time": None, 
            "shift_end_time": None,  
            "rate_type": job_data["rate_type"],  
            "hours_per_week": job_data["hours_per_day"],
            "salary_min_range": job_data["min_bill_rate"],  
            "salary_max_range": job_data["max_bill_rate"], 
            "benifits": None,
            "collaborate_members": None,
            "hiring_manager": hiring_manager,
            "cost_center_code": None,
            "additional_description": None,
            "interview_process": None,
            "work_locations": "{}",
            "work_locations_ex": get_work_location(job_data["location_id"]),
            "job_publish_date": publish_date, 
            "interview_questions": None,
            "source_job_url": None,
            "publish_status": "1",
            "source_id": "VMS-ALLGIESDEMO", 
            "skills": None
        }

        headers = {
            "Authorization":"NNqLko04zssteDeGJUnjLkW0VBLvIpcq7Kaa1wGOTnt",
            #"Content-Type":"application/json"
        }
        
        response = requests.post(url, data=data, headers=headers)
        job_board_data = response.json()
        job = Job.objects.get(pk=job_data["id"])
        job.job_board_id = job_board_data["result"]["id"]
        job.job_board_reference_number = job_board_data["result"]["job_reference_number"]
        job.save()

        return True
    except Exception as e:
        return False


def get_date(dates):
    dates = dates.split(" ")
    created_date = dates[0]
    publish_date = str(dates[0] + " "+dates[1].split(".")[0])
    return created_date, publish_date

def get_work_location(location_data):

    location_json = {}
    if location_data:
        location_json["city"] = location_data["city"]
        location_json["state"] = location_data["state"]
        location_json["country"] = location_data["country"]

    return location_json
   
