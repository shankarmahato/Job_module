from job.models import Job,JobCustom
from django.db.models import Q
from django.conf import settings
import requests
from rest_framework.response import Response
from django.core.paginator import Paginator
from job_distribution.models import VendorJobMapping
import os.path
import json
from simplify_job.cache import RedisCacheHandler
from job_catalog.models import *
from django.db import transaction

logger = settings.LOGGER
url_list = []
check_duplicate_url = {}


def get_filter_data(request):
    """
    Filtering data on the basis of any params, from column mapping
    """

    custom_columns = []
    and_condition = Q()
    filter_attrs = [arres for arres in request.GET]
    get_attrs = [f.name for f in Job._meta.get_fields()]
    custom_attrs_list = list(set(filter_attrs).difference(get_attrs))

    for keys, attrs_val in request.GET.items():
        if keys not in custom_attrs_list:
            if "order_by" in keys:
                pass
            if keys == "title":
                custom_columns.append({keys + "__title__icontains": attrs_val})
            elif keys == "template_name":
                custom_columns.append({keys + "__icontains": attrs_val})
            elif keys == "category":
                custom_columns.append({keys + "__category_name__icontains": attrs_val})
            elif keys != "title" and keys != "category":
                custom_columns.append({keys: attrs_val,})
        if "__" in keys:
            custom_columns.append({keys: attrs_val,})
    for dict_values in custom_columns:
        and_condition.add(Q(**dict_values), Q.AND)
    return and_condition

def stomp_connectivity(data, program_id):
    '''
    Connect with Approval Workflow
    '''
    try:
       
        approval_data = data[0]
        approval_data["program_id"] = program_id
        context = json.dumps(
            {
                "module":"job",
                "data": approval_data
            }
        )
        logger.info("Sending to submit approval")
        r = requests.post(settings.APPROVAL_WORKFLOW,
                          data=context, headers={'Content-Type': 'application/json'})
        r.raise_for_status()
        logger.info("Response from submit approval: {}".format(
            r.status_code
        ))
        if r.status_code == 202:
            return True
        else:
            return False
    except Exception as e:
        logger.error(e)
        return False

def get_program_name(request, program_id):
    token, ua = get_token_user_agent(request)
    program_details=None
    api_status = False
    try:
        url = settings.GET_PROGRAM_NAME.format(configurator_base_url=settings.CONFIGURATOR_BASE_URL, program_id=program_id)
        key = settings.PROGRAM_KEY.format(program_id)
        status, cache_data = get_redis_data(key)
        if status:
            try:
                program_details = cache_data['program']['name']
            except Exception as error:
                logger.error("Unable to read cache data of Program, {}".format(error))
                api_status = True

        else:
            api_status = True

        if api_status:
            logger.info("Sending request to configurator, url:{}".format(url))
            program_info_response = requests.get(url, headers={
                'Authorization': 'Bearer {}'.format(token),
                'user-agent': ua
            }, timeout=(settings.CONNECTIVITY,settings.RESPONSE_TIMEOUT))
            logger.info("Response from configurator: {}".format(
                program_info_response.status_code
            ))
            if program_info_response.status_code == 200:
                program_details = program_info_response.json()['program']['name']
        return program_details

            

    except Exception as e:
        logger.error("Error in Program, {}".format(e))
        return {}

class PaginationHandlerMixin(object):
    """
    Pagination mixin => helpful to set and get pagination.
    """
 
    @property
    def paginator(self):
        if not hasattr(self, "_paginator"):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class()
        else:
            pass
        return self._paginator
 
    def paginate_queryset(self, queryset):
        if self.paginator is None:
            return None
        return self.paginator.paginate_queryset(queryset, view=self)

def post_candidate(self, request):
    token, ua = get_token_user_agent(request)
    candidate_data = []

    try:
        
        candidate_payload = request.data["candidates"]
        if candidate_payload:
            for each_candidate in candidate_payload:
                vendor_id = each_candidate["vendor_id"]
                del each_candidate["vendor_id"]
                logger.info("candidate request - {}".format(each_candidate))
                url = settings.POST_CANDIDATES.format(configurator_base_url = settings.CONFIGURATOR_BASE_URL)
                candidate_info_response = requests.post(url, data=each_candidate, headers={
                    'Authorization': 'Bearer {}'.format(token),
                    'user-agent': ua
                })
                logger.info("candidate response - {}".format(candidate_info_response.status_code))
                if candidate_info_response.status_code != 201:
                    logger.info("candidate response - {}".format(candidate_info_response.text))
                else:
                    logger.info("candidate response - {}".format(candidate_info_response.json()))
                    candidate_info = candidate_info_response.json()
                    each_candidate["candidate_id"] = candidate_info["id"]
                    each_candidate["vendor_id"] = vendor_id
                    candidate_data.append(each_candidate)
        return candidate_data

    except Exception as e:
        logger.error("issue in candidate - {}".format(e))
        return candidate_data
        
def organization_id(request,program_id,user_id):

    token, ua = get_token_user_agent(request)
    api_status = False
    get_org_data = None  
    try:
        key = settings.USERS_KEY.format(program_id, user_id)
        status, cache_data = get_redis_data(key)
        if status:
            try:
                get_org_data = cache_data
            except Exception as error:
                logger.error("Unable to read cache data of Program, {}".format(error))
                api_status = True
        else:
            api_status = True
                                
        if api_status:
            member_url = settings.GET_USER.format(configurator_base_url = settings.CONFIGURATOR_BASE_URL, program_id = program_id, member_id = user_id)
            logger.info("Request Organization API, {}".format(member_url))
            org_info_response = requests.get(member_url, headers={
                        'Authorization': 'Bearer {}'.format(token),
                        'user-agent': ua
                    },timeout=(settings.CONNECTIVITY,settings.RESPONSE_TIMEOUT))
            logger.info("Response Organization API, {}".format(org_info_response))
            if org_info_response.status_code == 200:
                get_org_data = org_info_response.json()
    
        if get_org_data:
            get_org = get_org_data["member"]["organization"]
            if get_org:
                category = get_org["category"]
                organization_id = get_org["id"]
                if category == "Vendor":
                    job_list = list(VendorJobMapping.objects.filter(vendor_id=organization_id).values_list('job__id',flat=True))
                    if job_list:
                        return job_list
                    else:
                        return None
        else:
            return None
    except Exception as error:
        logger.error("Error in Member API - {}".format(str(error)))
        return None

def get_conf_json():
    data = []
    try:
        current_directory = os.path.dirname(__file__)
        path = os.path.split(current_directory)[0] + "/configurator_sample/configurator.json"
        with open(path) as f:
            conf = json.load(f)
        data = conf
        f.close()
        return data["config_json"]["config"]["field_groups"]
    except Exception as e:
        logger.error("Error in config_json - {}".format(str(e)))

def read_configurator_data(data):
    conf = {}
    custom_data = []
    custom_slug_name = []
    required_slug_name =[]
    required_data = []
    custom_status = False
    conf = get_conf_json()
    if len(conf)>=1:
        for each_conf in conf:
            conf_label = each_conf["label"]
            if 'Custom' in conf_label:
                custom_data = each_conf["fields"]
            elif 'Required' in conf_label:
                required_data = each_conf["fields"]
            else:
                return False, "Error in Configurator File", False
        

        # if catalog, template id in payload, title & category are not mandatory fields
        if 'catalog' in data:
            for each_fields in required_data:
                if each_fields["slug"] == "category":
                    each_fields.update({"is_required" : False  })

        if 'template' in data:
            for each_fields in required_data:
                if each_fields["slug"] == "category":
                    each_fields.update({"is_required" : False  })
                if each_fields["slug"] == "title":
                    each_fields.update({"is_required" : False  })

        if custom_data:
            custom_slug_name = [each_fields["slug"] for each_fields in custom_data]
        
        if required_data:
            required_slug_name = [each_fields["slug"] for each_fields in required_data]

        final_list = custom_slug_name + required_slug_name

        # Checking configurator Json
        # if not set([*data]).issubset(set(final_list)):
        #     return False, "Missing fields in configurator, {}".format(set([*data]).difference(set(final_list))), custom_status

        # Validating required fields
        check_required_fields = [each_required_field["slug"] for each_required_field in required_data if each_required_field["is_required"] ]
        check_required_fields.remove("uuid")
        check_required_data = set(check_required_fields).difference(set([*data]))  
        if check_required_data:
            return False, "Required fields missing, {}".format(check_required_data), custom_status

        # Validating custom fields
        check_custom_fields = [each_custom_field["slug"] for each_custom_field in custom_data if each_custom_field]
        check_custom_fields_new = [each_custom_field["slug"] for each_custom_field in custom_data if each_custom_field["is_required"]]
        check_custom_data = set(check_custom_fields_new).difference(set([*data]))  
        if check_custom_data and data['submit_type'] == "Submit":
            return False, "Required custom fields missing, {}".format(check_custom_data), custom_status

        # Mapping Custom Data (if any)
        if check_custom_fields_new and not check_custom_data:
            for each_custom_slug in custom_data:
                data[each_custom_slug["ref_column"]] = data[each_custom_slug["slug"]]
                del data[each_custom_slug["slug"]]
            custom_status = True

        data = check_additional_fields(data)

        return True, data, custom_status

def updated_custom_columns(all_data):
    """
    This method modified the custom column names with the
    mapping column data
    for e.g -
    {"column_1":"Python Developer"}   # Job Model
    {"column_1":"Job Title"}   # column mapping
    Output :
    {"Job title":"Python Developer"}
    """
    conf = get_conf_json()
    if len(conf)>=1:
        for each_conf in conf:
            conf_label = each_conf["label"]
            if 'Custom' in conf_label:
                custom_data = each_conf["fields"]

    get_column_name = [each_custom_field["slug"] for each_custom_field in custom_data]

    update_data= dict()
    for column in custom_data:
        all_data.update({column["slug"]:all_data[column["ref_column"]]})
        del all_data[column["ref_column"]]

    # Removing null values
    for keys, values in all_data.items():
        if 'column_' in keys and keys not in get_column_name:
            continue
        else:
            update_data.update({keys:values})

    return update_data

def check_additional_fields(data):

    if not "foundational_data" in data:
        data["foundational_data"]=[]
    if not "candidates" in data:
        data["candidates"]=[]
    if not "qualifications" in data:
        data["qualifications"]=[]
    if not "tags" in data:
        data["tags"]=[]
    return data

def get_token_user_agent(request):
    '''
    Function to get the token and user agent
    '''
    token = request.auth
    ua = request.META.get("HTTP_USER_AGENT", "SYSTEM")
    return token, ua
    
def retrieve_custom_columns(alldata):
    """
    This method modified the custom column names with the
    mapping column data
    for e.g -
    Input :
    {"Job title":"Python Developer"}
    Output:
    {"column_1":"Python Developer"}   # Job Model
    {"column_1":"Job Title"}   # column mapping
    """
    new_data = alldata
    conf = get_conf_json()
    if len(conf)>=1:
        for each_conf in conf:
            conf_label = each_conf["label"]
            if 'Custom' in conf_label:
                custom_data = each_conf["fields"]
    get_dict = {}
    
    for each_custom_field in custom_data:
        get_dict[each_custom_field["slug"]] = each_custom_field["ref_column"]

    for newkey, value in get_dict.items():
        if newkey in alldata:
            alldata[value] =  alldata[newkey]
            del alldata[newkey]

    
    return alldata

def approval_conf_json():
    data = []
    try:
        current_directory = os.path.dirname(__file__)
        path = os.path.split(current_directory)[0] + "/configurator_sample/configurator.json"
        with open(path) as f:
            conf = json.load(f)

        data = conf
        f.close()
        return data["config_json"]["config"]["approvals"]
    except Exception as e:
        logger.error("Error in approval_config_json - {}".format(str(e)))

def read_approval_conf_json():
    conf = {}
    custom_slug_name = []
    conf = approval_conf_json()
    if len(conf)>=1:
        for each_conf in conf:
            approval_data = each_conf["fields"]

        if approval_data:
            custom_slug_name = [each_fields["slug"] for each_fields in approval_data]

    return custom_slug_name

def validate_approval(data):
    approval_conf_data = read_approval_conf_json()
    status = False

    if approval_conf_data:
        for keys in data:
            if keys in approval_conf_data:
                status =  True
                break

    return status

def set_redis_data(data, key, program_id):
    cache_key = 'program:{}:key:{}'.format(program_id, key)
    logger.info('setting cache data of key: {}'.format( key))
    RedisCacheHandler.set(cache_key, data)
    return True

def get_redis_data(key):
    status = False
    cache_data  = RedisCacheHandler.get(key)
    if cache_data:
        status = True
        logger.info('getting cache data of key: {}: data: {}'.format( key, cache_data))
    else:
        logger.error('unable to get cache data of key: {}: data: {}'.format( key, cache_data))

    return status, cache_data

def submit_candidate(request, candidate_data, job_id, program_id):
    
    #  CANDIDATE SUBMIT API
    token, ua = get_token_user_agent(request)
    data = {  "candidates": candidate_data }
    logger.info('Request Submitting candidates Job Id: {}: data: {}'.format( job_id, data))
    url = settings.SUBMIT_CANDIDATES.format(configurator_base_url=settings.CONFIGURATOR_BASE_URL, program_id=program_id, job_id=job_id)
    logger.info('Request Submitting candidates url: {}'.format(url))
    response_candidate= requests.post(url ,
                          data=json.dumps(data), headers={
                              'Content-Type': 'application/json',
                              'Authorization': 'Bearer {}'.format(token),
                              'user-agent': ua
                              })
    logger.info('Response Submitting candidates {}'.format( response_candidate ))

    if response_candidate.status_code == 201:
        logger.info('Response --- submission id {}'.format( response_candidate.json ))
        return True
    else:
        return False

def notification_email(job_obj, program_id):

    context = json.dumps({"program_id": program_id,
                            "category": "job",
                            "event": "job create",
                            "actor": "client/msp",
                            "data": job_obj[0]
                            })
    logger.info('Context: %s', context)
    r = requests.post(settings.NOTIFICATION_API,
                        data=context, headers={'Content-Type': 'application/json'})
    if r.status_code == 202:
        logger.info("Notification Send of Job: {}".format(r.status_code))
        return True
    else:
        logger.error("Error while submitting: {}".format(r.status_code))
        return False

def update_checklist_onboarding(checklist_data, request, program_id, job_id):

    token, ua = get_token_user_agent(request)
    try:
        for each_ids in checklist_data["id"]:
            url = settings.VALIDATE_CHECKLIST.format(configurator_base_url=settings.CONFIGURATOR_BASE_URL,program_id=program_id, checklist_id=each_ids, job_id=job_id)
            logger.info(
                "ONBOARDING CHECKLIST >> PUT >> request: {}, url- {} ".format(
                    each_ids, url))
            response = requests.put(url, data={}, headers= {
                                'Content-Type': 'application/json',
                                'Authorization': 'Bearer {}'.format(token),
                                'user-agent': ua
                                })
            logger.info(
                "ONBOARDING CHECKLIST >> PUT >> response: {}".format(response.status_code))

            if response.status_code == 200:
                logger.info("Checklist Updated -- {}".format(response.json()))
                return True
            else:
                logger.info("Checklist not updated -- {}".format(response.text))
                return False
    except Exception as e:
        logger.error("Issue in updating checklist -- {}".format(e))
        return False

def validate_checklist_data(checklist_data, request, program_id):
    token, ua = get_token_user_agent(request)
    if isinstance(checklist_data, dict):
        if "id" in checklist_data:
            if checklist_data["id"]:
                for each_ids in checklist_data["id"]:
                    url = settings.CHECKLIST.format(configurator_base_url=settings.CONFIGURATOR_BASE_URL,program_id=program_id, checklist_id=each_ids)
                    logger.info("Request Checklist Validate -- {}".format(url))
                    resp = requests.get(url, headers={
                                    'Content-Type': 'application/json',
                                    'Authorization': 'Bearer {}'.format(token),
                                    'user-agent': ua
                                    }, 
                    timeout=(settings.CONNECTIVITY,settings.RESPONSE_TIMEOUT))
                    res_status_code  = resp.status_code
                    if res_status_code == 200:
                        logger.info("Checklist Validated!")
                        logger.info("Reponse -- {}".format(resp.json()))
                        return True, resp.json()
                    else:
                        logger.info("Reponse -- {}".format(resp.text))
                        return False, resp.text
            else:
                logger.error("Checklist is required")
                return False, "Checklist is required"

        else:
            logger.error("Invalid format for checklist")
            return False, "Invalid format for checklist"
    else:
        logger.error("Invalid format for checklist")
        return False, "Invalid format for checklist"


def job_from_template(job_obj):

    status = False
    msg = None
    template_obj = job_obj['template']
    job_obj['source'] = 'Template'
    job_obj['source_id'] = job_obj['template']
    try:
        template_data = Job.objects.filter(uid=template_obj, is_delete=False, is_template=True)
        if not template_data:
            msg = "{} not found".format(template_obj)
        else:
            job_obj['title'] = template_data[0].title.id
            job_obj['category'] = template_data[0].category.id
            job_obj['template'] = template_data[0].id
            status = True
    except Exception as e:
        logger.error("Error in catalog query, {}".format(e))
        msg = e 
    return job_obj, status, msg


def job_from_catalog(job_obj):
    
    status = False
    msg = None
    catalog_obj = job_obj['catalog']
    job_obj['source'] = 'Catalog'
    job_obj['source_id'] = catalog_obj
    try:
        catalog_obj = JobCatalog.objects.get(uid=catalog_obj)
        job_obj['category'] = catalog_obj.category.id
        status = True
    except Exception as e:
        logger.error("Error in catalog query, {}".format(e))
        msg = e 

    return job_obj, status, msg


def get_uid(job_obj):

    '''
    converting uid to id
    '''
    status = False
    msg = None
    try:

        if 'category' in job_obj:
            category_obj = JobCategory.objects.get(uid = job_obj['category'])
            job_obj['category'] = category_obj.id
        if 'title' in job_obj:
            title_obj = JobTitle.objects.get(uid = job_obj['title'])
            job_obj['title'] = title_obj.id
        status = True
    except Exception as e:
        logger.error("Error in uid {}".format(e))
        msg = e

    return job_obj, status, msg






def add_job_id(job_data, program_name):

    status = False
    msg = None  

    if not program_name:
        status = True
        msg = "Program Name cannot be blank -- {}".format(program_name)
    else:
        with transaction.atomic():
            try:
                job_obj = Job.objects.filter(program_id=job_data.program_id, 
                                                id__lte=job_data.id, 
                                                is_template=job_data.is_template)
                count_jobs_all = job_obj.count()
                count_job = 1
                if count_jobs_all > 1:
                    job_id_data = job_obj[count_jobs_all-2].job_id
                    if  job_id_data:
                        count_job = job_id_data.split('-')
                        count_job  = int(count_job[-1]) + 1 

                if job_data.is_template:
                    job_type = "JT"
                else:
                    job_type = "JB"

                job_id = "{}-{}-{}".format(job_type, program_name.upper(), '{0:03}'.format(count_job))
                logger.info("JOB ID created -- {}, uid - {}".format(job_id, job_data.uid)) 
                job_obj.filter(id=job_data.id).update(job_id=job_id)
            except Exception as e:
                logger.error(e)
                instance = Job.objects.get(id=job_data.id)
                instance.delete()
                status = True
                msg = e

    return status, msg
