from job.models import Job,JobCustom,JobConfiguration,FoundationData,TalentNeuron,FoundationQualificationData
from django.conf import settings
from job.utils import updated_custom_columns, get_token_user_agent
import datetime
import requests
from .utils import url_list, check_duplicate_url
logger = settings.LOGGER


def retrieve_jobs(program_id, queryset, request, uid=None):
    
    final_list = []
    if uid:
        job_detail_status = True
    else:
        job_detail_status = False

    for each_jobs in queryset:

        # Url for Members api
        users_check(each_jobs, program_id)
        custom_data = custom_dict(each_jobs)
        data =  {
                    "id": each_jobs.id,
                    "uid": str(each_jobs.uid),
                    "job_id": each_jobs.job_id,
                    "job_manager": each_jobs.job_manager,
                    "msp_manager": each_jobs.msp_manager,
                    "title": {
                        "id": each_jobs.title.id,
                        "uid": each_jobs.title.uid,
                        "title":  each_jobs.title.title,
                        "level": each_jobs.title.level,
                        "description": each_jobs.title.description,
                        "job_tag": get_manytomany_data(each_jobs.title.job_tag)
                    },
                    "category": {
                        "id": each_jobs.category.id,
                        "uid": each_jobs.category.uid,
                        "o_net_soc_code": each_jobs.category.o_net_soc_code,
                        "category_name": each_jobs.category.category_name,
                        "description": each_jobs.category.description
                    },
                    "type": each_jobs.type,
                    "hire_type": each_jobs.hire_type,
                    "company_name": each_jobs.company_name,
                    "level": each_jobs.level,
                    "no_of_openings": each_jobs.no_of_openings,
                    "rate": each_jobs.rate,
                    "rate_type": each_jobs.rate_type,
                    "hours_per_day": each_jobs.hours_per_day,
                    "total_hours": each_jobs.total_hours,
                    "total_days": each_jobs.total_days,
                    "additional_amount": each_jobs.additional_amount,
                    "adjustment_type": each_jobs.adjustment_type,
                    "allow_expense": each_jobs.allow_expense,
                    "assignment_length": each_jobs.assignment_length,
                    "min_budget": each_jobs.min_budget,
                    "max_budget": each_jobs.max_budget,
                    "adjustment_value": each_jobs.adjustment_value,
                    "location_id": get_location(each_jobs, True),
                    "description": each_jobs.description,
                    "start_date": str(each_jobs.start_date),
                    "end_date": str(each_jobs.end_date),
                    "hierarchy": get_hierarchy(each_jobs, True),
                    "hierarchy_location": each_jobs.hierarchy_location,
                    "budget_estimate": each_jobs.budget_estimate,
                    "currency": each_jobs.currency,
                    "min_bill_rate": each_jobs.min_bill_rate,
                    "max_bill_rate": each_jobs.max_bill_rate,
                    "shift": each_jobs.shift,
                    "distribution": each_jobs.distribution,
                    "shift_calender": each_jobs.shift_calender,
                    "pre_identified_candidate": each_jobs.pre_identified_candidate,
                    "pre_identified_vendor": each_jobs.pre_identified_vendor,
                    "schedule_interview": each_jobs.schedule_interview,
                    "response_by_date": str(each_jobs.response_by_date),
                    "approve": each_jobs.approve,
                    "is_template": each_jobs.is_template,
                    "template_name": each_jobs.template_name,
                    "template":  each_jobs.template.id if each_jobs.template else None,
                    "qualifications": get_qualifications(each_jobs, job_detail_status),
                    "tags":get_manytomany_data(each_jobs.tags),
                    "created_by": each_jobs.created_by,
                    "modified_by": each_jobs.modified_by,
                    "is_delete": each_jobs.is_delete,
                    "status": each_jobs.status,
                    "submit_type":each_jobs.submit_type,
                    "candidate": get_candidate(each_jobs, job_detail_status),
                    "foundational_data": get_foundational_data(each_jobs, job_detail_status),
                    "checklist": get_checklist_url(each_jobs, job_detail_status),
                    "trigger_approval_workflow": each_jobs.trigger_approval_workflow,
                    "unit_of_measure": each_jobs.unit_of_measure,
                    "note_for_approver": each_jobs.note_for_approver,
                    "vendor_rate_exceed": each_jobs.vendor_rate_exceed,
                    "approverlist": get_approver(each_jobs, job_detail_status),
                    "check_max_bill_rate": each_jobs.check_max_bill_rate,
                    "job_board_id": each_jobs.job_board_id,
                    "job_board_reference_number": each_jobs.job_board_reference_number,
                    "rate_model": each_jobs.rate_model,
                    "ot_exempt": each_jobs.ot_exempt,
                    "allow_user_description": each_jobs.allow_user_description,
                    "created_on":str(each_jobs.created_on),
                    "modified_on":str(each_jobs.modified_on),
                    "is_enabled": each_jobs.is_enabled,
                    "submissions_from_direct_sourcing": each_jobs.submissions_from_direct_sourcing,
                    "automatic_distribution":each_jobs.automatic_distribution,
                    "submission_limit_vendor":each_jobs.submission_limit_vendor,
                    "automatic_distribute_submit":each_jobs.automatic_distribute_submit,
                    "automatic_distribute_final_approval":each_jobs.automatic_distribute_final_approval,
                    "tiered_distribute_schedule":each_jobs.tiered_distribute_schedule,
                    "distribute_schedule":each_jobs.distribute_schedule,
                    "immediate_distribution":each_jobs.immediate_distribution,
                    "after_immediate_distribution":each_jobs.after_immediate_distribution,
                    "manual_distribution_job_submit":each_jobs.manual_distribution_job_submit,
                    "submission_exceed_max_bill_rate":each_jobs.submission_exceed_max_bill_rate,
                    "source": each_jobs.source,
                    "source_id": each_jobs.source_id,
                    "column_1": custom_data["column_1"],
                    "column_2": custom_data["column_2"],
                    "column_3": custom_data["column_3"],
                    "column_4": custom_data["column_4"],
                    "column_5": custom_data["column_5"],
                    "column_6": custom_data["column_6"],
                    "column_7": custom_data["column_7"],
                    "column_8": custom_data["column_8"],
                    "column_9": custom_data["column_9"],
                    "column_10": custom_data["column_10"],
                    "history": get_history(each_jobs, job_detail_status)
        }
        updated_data = updated_custom_columns(data)

        final_list.append(updated_data)

    return final_list
        

def get_location(obj, status):
    '''
    To get Work location
    '''

    list_location = ["0", "", None]
    if status and obj.location_id not in list_location:
            
        url = [settings.WORK_LOCATION.format(configurator_base_url = settings.CONFIGURATOR_BASE_URL, program_id = obj.program_id, location_id = obj.location_id)]
        
        # Validating the url to remove redundancy 
        list_key = str(obj.location_id)+"-"+"location_id"
        if list_key not in check_duplicate_url:
            check_duplicate_url[list_key] = {
                'url': url
                }

        url_list.append({
                    'job_id': obj.id,
                    'dict_key': 'location_id',
                    'url': url,
                    'id': {"id1":obj.location_id}
                    })
        return url
    else:
        return obj.location_id


def get_hierarchy(obj, status):
    '''
    To get the hierarchies
    '''
    if status and obj.hierarchy:
        url = [settings.HIERARCHY.format(configurator_base_url = settings.CONFIGURATOR_BASE_URL, program_id = obj.program_id, hierarchy_id = obj.hierarchy)]
        # Validating the url to remove redundancy 
        list_key = str(obj.hierarchy)+"-"+"hierarchy"
        if list_key not in check_duplicate_url:
            check_duplicate_url[list_key] = {
                'url': url
                }

        url_list.append({
            'job_id': obj.id,
            'dict_key': 'hierarchy',
            'url': url,
            'id': {"id1":obj.hierarchy}
            })
        return url
    else:
        return []
        
def get_approver(obj, status):
    if status == True:
        url = [settings.APPROVAL.format(approval_base_url=settings.APPROVAL_LIST, job_id = obj.id)]
        url_list.append({
            'job_id': obj.id,
            'dict_key': 'approverlist',
            'url': url,
            'id':{}
            })
        
        return url
    else:
        return []

def get_checklist_url(obj, status):
    final_list = []
    if status:
        if obj.checklist:
            try:
                for each_ids in obj.checklist["id"]:
                    url = settings.CHECKLIST.format(configurator_base_url=settings.CONFIGURATOR_BASE_URL,program_id=obj.program_id, checklist_id=each_ids)
                    final_list.append(url)
                    url_list.append({
                        'job_id': obj.id,
                        'dict_key': 'checklist',
                        'url': [url],
                        'id': {"id1": each_ids}
                        })
            except Exception as e:
                logger.error("issue in checklist -- {} ". format(obj.checklist))
                return final_list
    else:
        final_list.append(obj.checklist)
    return final_list


def get_candidate(obj, status):
    if status:
        url = settings.GET_JOB_CANDIDATES.format(configurator_base_url=settings.CONFIGURATOR_BASE_URL, program_id=obj.program_id, job_id=obj.uid)
        url_list.append({
            'job_id': obj.id,
            'dict_key': 'candidate',
            'url': [url],
            'id': {"id1": obj.uid }
            })
        return  url
    else:
        return []


def get_qualifications(obj, status):
        id = obj.id
        qs = FoundationQualificationData.objects.filter(job__id=id, entity_name="qualification")
        q_id = qs.values_list('entity_id', flat=True).distinct()

        qualification_list=[]
        try:
            if q_id:
                if status:

                    for qualification in q_id:
                        qsa = qs.filter(entity_id=qualification)
                        skill_id = qsa.values_list('entity_key', flat=True).distinct()
                        for skills in skill_id:
                            url = settings.QUALIFICATION.format(
                                configurator_base_url=settings.CONFIGURATOR_BASE_URL, program_id=obj.program_id, qualification_type_id=qualification, qualification_id=skills)

                            if skills:

                                # Validating the url to remove redundancy 
                                list_key = str(qualification)+"-"+str(skills)+"-"+"qualifications"
                                if list_key not in check_duplicate_url:
                                    check_duplicate_url[list_key] = {
                                        'url': url
                                        }

                                qualification_list.append(url)
                                url_list.append({
                                    'job_id': obj.id,
                                    'dict_key': 'qualifications',
                                    'url': [url],
                                    'id': {"id1": qualification, "id2": skills }
                                    })
                else:
                    for qualification in qs:
                        qualifications = (
                        {'qualification_type_id': qualification.entity_id, 'qualification_type': qualification.entity_type,
                        'values': []})
                        qsa = qs.filter(entity_id=qualification.entity_id)
                        for skills in qsa:
                            qualifications['values'].append({"id": skills.entity_key, "level": skills.entity_value})
                        qualification_list.append(qualifications)

                    qualification = list({v['qualification_type_id']: v for v in qualification_list}.values())
                    return qualification

        except Exception as e:
            logger.error("Unable to retrieve Qualifications, {}".format(e))
        return qualification_list


def get_foundational_data(obj, status):
    foundational_list = []
    id = obj.id
    qs = FoundationQualificationData.objects.filter(job__id=id, entity_name="foundational")
    logger.info('FoundationQualificationData queryset {}'.format(qs))
    try:
        if qs: 
            if status:
                for foundational in qs:
                    qsa = qs.filter(entity_id=foundational.entity_id)
                    for code in qsa:
                        url = settings.FOUNDATION_DATA.format(
                            configurator_base_url=settings.CONFIGURATOR_BASE_URL, program_id=obj.program_id, foundation_type_id=foundational.entity_id,foundation_id=code.entity_key)
                        if code.entity_key:
                            
                            # Validating the url to remove redundancy 
                            list_key = str(foundational.entity_id)+"-"+str(code.entity_key)+"-"+"foundational_data"
                            if list_key not in check_duplicate_url:
                                check_duplicate_url[list_key] = {
                                    'url': url
                                    }

                            url_list.append({
                                'job_id': obj.id,
                                'dict_key': 'foundational_data',
                                'url': [url],
                                'id': {"id1": foundational.entity_id, "id2": code.entity_key }
                                })
                            foundational_list.append(url)
            else:
                for foundational in qs:
                    foundationals = ({'foundational_data_type_id': foundational.entity_id, 'values': []})
                    qsa = qs.filter(entity_id=foundational.entity_id)
                    for skills in qsa:
                        foundationals['values'].append({"id": skills.entity_key})
                    foundational_list.append(foundationals)

                final_list = list({v['foundational_data_type_id']: v for v in foundational_list}.values())


                return final_list

    except Exception as e:
        logger.error("Unable to retrieve Foundational Data, {}".format(e))


    
    return foundational_list


def get_custom_columns(obj):
    try:
        job_data = JobCustom.objects.get(job__id=obj.id)
        return True, job_data
    except JobCustom.DoesNotExist:
        return False,None


def custom_dict(obj):
    status, data = get_custom_columns(obj)
    return {
        "column_1": data.column_1 if status else None,
        "column_2": data.column_2 if status else None,
        "column_3": data.column_3 if status else None,
        "column_4": data.column_4 if status else None,
        "column_5": data.column_5 if status else None,
        "column_6": data.column_6 if status else None,
        "column_7": data.column_7 if status else None,
        "column_8": data.column_8 if status else None,
        "column_9": data.column_9 if status else None,
        "column_10": data.column_10 if status else None
    } 


def get_history(obj, status):
    history = []
    if status:
        job_id = obj.id
        try:
            job_data = Job.objects.get(id=job_id)
        except Job.DoesNotExist:
            logger.error("Job with id = %s does not exist", job_id)
        try:
            job_history = job_data.history.all()
            if len(job_history) > 1:
                history_list = [[x,y] for x,y in zip(job_history[:len(job_history)], job_history[1:])]
                for each in history_list:
                    new_record, old_record = each
                    delta = new_record.diff_against(old_record)
                    for change in delta.changes:
                        if (isinstance(change.old,datetime.datetime)):
                                change.old = change.old.strftime('%Y-%m-%dT%I:%M:%SZ')
                        changes = {change.field : change.old}
                        #changes = "{} changed from {} to {}".format(change.field, change.old, change.new)
                        history.append(changes)
        except Exception as e:
            logger.error("Job {} , issue in history - {}".format(job_id, e))

    return history


def get_manytomany_data(obj):
    tags_list = []
    tags_data = obj.values_list()
    if tags_data:
        for each_tags in obj.values_list():
            tags_dict = {}
            tags_dict["id"] = each_tags[0]
            tags_dict["tag"] = each_tags[1]
            tags_list.append(tags_dict)
    return tags_list


def users_check(obj, program_id):
    '''
    To get the member details
    '''
    list_users = [obj.job_manager, obj.msp_manager, obj.created_by, obj.modified_by]
    final_list = list(set(list_users))
    for each_user in final_list:
        if each_user:
            url = [settings.GET_USER.format(configurator_base_url=settings.CONFIGURATOR_BASE_URL, program_id=program_id, member_id=each_user)]
            # Validating the url to remove redundancy 
            list_key = str(each_user)+"-"+"users"
            if list_key not in check_duplicate_url:
                check_duplicate_url[list_key] = {
                    'url': url
                    }
                    
            url_list.append({
                    'job_id': obj.id,
                    'dict_key': "users",
                    'url': url,
                    'id': {"id1":each_user}
            })
    if all(list_users):
        return True
    else:
        return False

