from job.models import Job,JobCustom,JobConfiguration,FoundationData,TalentNeuron,FoundationQualificationData
from django.conf import settings
logger = settings.LOGGER

def update_response_data(query_data, data, uid):
    for each_data in data:
        index = search_index(query_data, each_data["job_id"])
        if index == None:
            continue

        dict_key = each_data["dict_key"]
        content = each_data["content"]
        status_code = each_data["status_code"]
        url = each_data["url"]

        if dict_key == "users":
            query_data = get_user_data(query_data, each_data, index, uid)

        elif dict_key == "location_id":
            if status_code==200:
                query_data[index][dict_key] =  content["work_location"] 
            else:
                query_data[index][dict_key]={}
        elif dict_key == "approverlist":
            if status_code==200:
                query_data[index][dict_key] =  content["data"]["approvals"]
            else:
                query_data[index][dict_key] = []
        elif dict_key == "hierarchy":
            if status_code==200:
                query_data[index][dict_key] =  content["hierarchy"]
            else:
                query_data[index][dict_key]=[]
        elif dict_key == "checklist":
            inside_list = get_list(query_data[index][dict_key], url[0])
            if inside_list is not None:
                if status_code == 200:
                    try:
                        query_data[index][dict_key][inside_list] = content["checklist"]
                    except Exception as e:
                        logger.error("checklist error {}".format(e))
                else:
                    obj = Job.objects.get(id=each_data["job_id"])
                    query_data[index][dict_key][inside_list] = obj.checklist


        elif dict_key == "candidate":
            # inside_list = get_list(query_data[index][dict_key], url[0])
            # if inside_list is not None:
            if status_code == 200:
                try:
                    query_data[index][dict_key] = content["candidates"] 
                except Exception as e:
                    logger.error("Candidate error {}".format(e))
            else:
                query_data[index][dict_key]=[]


        elif dict_key == "qualifications":
            qs = FoundationQualificationData.objects.filter(job__id=each_data["job_id"], entity_name="qualification")
            q_id = qs.values_list('entity_id', 'entity_type').distinct()
            try:
                inside_list = get_list(query_data[index][dict_key], url[0])
                Flag = False
                if q_id and inside_list is not None:
                    for qualification_obj in q_id:
                        qualification = qualification_obj[0]
                        entity_type = qualification_obj[1]
                        qsa = qs.filter(entity_id=qualification)
                        skill_id = qsa.values_list('entity_key', flat=True).distinct()
                        qualifications = (
                            {'qualification_type_id': qualification, 'qualification_type': entity_type,
                            'values': []})
                        for skills in skill_id:
                            skills_set = qs.filter(entity_key=skills, entity_id=qualification).last()
                            if qualification  in url[0] and skills in url[0]:
                                try:
                                    if status_code == 200:
                                        qualification_info = content
                                        qualification_info = qualification_info['qualification']['name']
                                        qualifications['values'].append({"id": skills_set.entity_key, "level": skills_set.entity_value,"name":qualification_info, "is_active":skills_set.entity_is_active})
                                    else:
                                        qualifications['values'].append({"id": skills_set.entity_key, "level": skills_set.entity_value, "is_active":skills_set.entity_is_active})
                                    Flag = True
                                    
                                except Exception as e:
                                    logger.error("Qualification error {}".format(e))
                        if Flag:
                            query_data[index][dict_key][inside_list] = qualifications
                            break

            except Exception as e:
                logger.error("Qualification error {}".format(e))

        elif dict_key == "foundational_data":
            id = each_data["job_id"]
            qs = FoundationQualificationData.objects.filter(job__id=id, entity_name="foundational")
            try:
                inside_list = get_list(query_data[index][dict_key], url[0])
                foundational_data_dict = {}
                if qs and inside_list is not None:
                    for foundational in qs:
                        qsa = qs.filter(entity_id=foundational.entity_id)
                        for code in qsa:
                            if foundational.entity_id  in url[0] and code.entity_key in url[0]:
                                foundational_data_dict['foundational_data_type_id'] = foundational.entity_id
                                try:
                                    if status_code == 200:
                                        foundational_info = content
                                        foundational_data_dict['values'] = foundational_info
                                    else:
                                        foundational_data_dict['values'] = {"id": code.entity_key}

                                except Exception as e:
                                    logger.error("Foundational error {}".format(e))
                    query_data[index][dict_key][inside_list] = foundational_data_dict

            except Exception as e:
                logger.error("Foundational error {}".format(e))

    return query_data


def search_index(query_data, id):
    status = False
    each_jobs ={}
    for each_jobs in query_data:
        job_id = each_jobs["id"]
        if id == job_id:
            status = True
            break  
    if status:
        return query_data.index(each_jobs)
    else:
        return None
    


def get_user(user_data):
    if "member" in user_data:
        data = user_data["member"]
        if 'id' in data:
            return {'id': data["id"],
            'first_name': data["first_name"],
            'last_name': data["last_name"],
            'email': data["email"]
            }
        else:
            return {}
    else:
        return {}

def get_list(urls_list, url):
    try:
        index_list = urls_list.index(url)
    except Exception as e:
        logger.error(e)
        index_list = None

    return index_list

def get_user_data(query_data, data, index, uid):

    status_code = data["status_code"]
    user_id = data["id"]["id1"]
    if status_code == 200:
        content = get_user(data["content"])
    else:
        content = user_id
    
    
    if query_data[index]["job_manager"] == user_id and status_code==200:
        query_data[index]["job_manager"] = content
    if query_data[index]["msp_manager"] == user_id and status_code==200 and uid:
        query_data[index]["msp_manager"] = content
    if query_data[index]["created_by"] == user_id and status_code==200 and uid:
        query_data[index]["created_by"] = content
    if query_data[index]["modified_by"] == user_id and status_code==200 and uid:
        query_data[index]["modified_by"] = content
    return query_data










