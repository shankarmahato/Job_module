import json

import requests
from django.conf import settings

from simplify_job.cache import RedisCacheHandler


def get_auth_token():
    """
    Function will return the token based on the username and
    password provided.
    """
    payload = {
        "username": settings.AUTH_TOKEN_USERNAME,
        "password": settings.AUTH_TOKEN_PASSWORD
    }
    headers = {
        "Content-Type": "application/json",
        'user-agent': 'SYSTEM'
    }
    try:
        response = requests.post(
            settings.AUTH_TOKEN_ENDPOINT,
            data=json.dumps(payload),
            headers=headers,
            timeout=(settings.CONNECTIVITY, settings.RESPONSE_TIMEOUT)
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as error:
        raise Exception(
            'error: could not get content from url because of {}'.format(
                response.status_code))
    except requests.exceptions.ConnectTimeout:
        raise Exception(
            'error: requests.exceptions.ConnectTimeout while  {}'.format(
                "getting auth_token"))

    return response.json()['token']


def map_distribute_type(distribute_type):
    context = {
        'manual': [],
        'scheduled': ["distribution_id"],
        'automatic': [
            "distribute_method",
            "vendor_selection"
        ]
    }
    return context[distribute_type]


def get_vendors_based_on_group_id(request, endpoint, program_id, group_id):
    '''
    Returns Vendor_group data based on group_id_list
    provided.
    '''
    headers = {
        'Authorization': request.headers["Authorization"]
    }

    content_type = request.headers.get("Content-Type")
    user_agent = request.headers.get("User-Agent")

    if content_type:
        headers["Content-Type"] = content_type

    if user_agent:
        headers["User-Agent"] = user_agent

    url_dict = {
        "configurator_base_url": endpoint,
        "program_id": program_id,
        "group_id": group_id
    }

    url = settings.GET_VENDORS_BASED_ON_GROUP_ID.format(**url_dict)

    cache_key = 'svms:job-manager:programs:{}:vendor-groups:{}'.format(
        program_id, group_id)

    cache_data = RedisCacheHandler.get(cache_key)

    if cache_data:
        return cache_data['vendor_groups']['vendors']
    else:
        # url = "https://dev-services.simplifysandbox.net/configurator/programs/ecb4d785-5b17-4546-8ed2-ca1a3f0cc653/vendor-groups/9b8226eb-37c8-47bd-9f9e-33bdf02c9841"

        try:
            response = requests.get(
                url, headers=headers,
                timeout=(settings.CONNECTIVITY, settings.RESPONSE_TIMEOUT))
            response.raise_for_status()
        except requests.exceptions.HTTPError as error:
            raise Exception(
                'error: could not get content from url because of {}'.format(
                    response.status_code))
        except requests.exceptions.ConnectTimeout:
            raise Exception(
                'error: requests.exceptions.ConnectTimeout while  {}'.format(
                    "getting vendors based on group id"))

        RedisCacheHandler.set(cache_key, response.json())

        return response.json()['vendor_groups']['vendors']


def get_vendor_details(request, endpoint, vendor_id):
    '''
    Returns Vendor_group data based on group_id_list
    provided.
    '''
    # vendor_id = "52b42aee-4680-49b7-9897-db26be8e7354"
    url_dict = {
        "configurator_base_url": endpoint,
        "vendor_id": vendor_id
    }
    # url = '{}/organizations/{}'.format(endpoint, vendor_id)
    url = settings.GET_VENDOR_DETAIL.format(**url_dict)

    headers = {
        'Authorization': request.headers["Authorization"]

    }

    content_type = request.headers.get("Content-Type")
    user_agent = request.headers.get("User-Agent")

    if content_type:
        headers["Content-Type"] = content_type

    if user_agent:
        headers["User-Agent"] = user_agent

    cache_key = 'svms:job-manager:organizations:{}'.format(vendor_id)

    cache_data = RedisCacheHandler.get(cache_key)

    if cache_data:
        return cache_data
    else:
        try:
            # url = "http://dev-awsnlb.simplifyvms.com:8003/configurator/organizations/52b42aee-4680-49b7-9897-db26be8e7354"
            response = requests.get(
                url, headers=headers,
                timeout=(settings.CONNECTIVITY, settings.RESPONSE_TIMEOUT))
            response.raise_for_status()
        except requests.exceptions.HTTPError as error:
            raise Exception(
                'error: could not get vendor details from url {}  because of {}'.format(
                    url, response.status_code))
        except requests.exceptions.ConnectTimeout:
            raise Exception(
                'error: requests.exceptions.ConnectTimeout while  {}'.format(
                    "getting vendor details"))

        RedisCacheHandler.set(cache_key, response.json())
        return response.json()


def get_vendors(request, endpoint, program_id):
    '''
    Return program_vendors data to fetch vendor list
    based on program_id and industry list
    '''

    # token = get_auth_token()
    # headers = {
    #     'Authorization': 'Bearer {}'.format(token),
    #     "Content-Type": "application/json",
    #     'user-agent': 'SYSTEM'
    # }

    headers = {
        'Authorization': request.headers["Authorization"]

    }

    content_type = request.headers.get("Content-Type")
    user_agent = request.headers.get("User-Agent")

    if content_type:
        headers["Content-Type"] = content_type

    if user_agent:
        headers["User-Agent"] = user_agent

    url_dict = {
        "configurator_base_url": endpoint,
        "program_id": program_id
    }

    # url = '{}/programs/{}/vendors'.format(endpoint, program_id)
    url = settings.GET_VENDORS.format(**url_dict)

    try:
        response = requests.get(url, headers=headers,
                                timeout=(settings.CONNECTIVITY,
                                         settings.RESPONSE_TIMEOUT))
        response.raise_for_status()
    except requests.exceptions.HTTPError as error:
        raise Exception(
            'error: could not get content from url because of {}'.format(
                response.status_code))
    except requests.exceptions.ConnectTimeout:
        raise Exception(
            'error: requests.exceptions.ConnectTimeout while  {}'.format(
                "getting vendor"))

    return response.json()['program_vendors']


def map_vendor_dict(request,
                    program_id, job_id, distribute_type, vendor_id_data_list,
                    distribute_method=None, vendor_selection=None,
                    submission_limit=None, is_vendor_group_data=False):
    '''
    Prepare list object to give it to serializer for adding
    data based on vendor_id and vendor_group_id
    '''
    vendor_id_obj_list = []

    if is_vendor_group_data:
        for vendor_group_id in vendor_id_data_list:
            try:
                vendor_list = get_vendors_based_on_group_id(
                    request,
                    settings.VENDOR_ENDPOINT,
                    program_id,
                    vendor_group_id
                )
            except Exception as error:
                settings.LOGGER.error(
                    "map_vendor_dict >> post >> Problem fetching Vendor: error: {} {}".format(
                        error,
                        vendor_group_id
                    ))
                continue

            for v_id in vendor_list:
                context = {
                    'program_id': program_id,
                    'job_id': job_id,
                    'distribute_type': distribute_type,
                    'vendor_id': v_id["id"],
                    'vendor_group_id': vendor_group_id
                }
                if submission_limit is not None:
                    context.update({
                        "submission_limit": submission_limit
                    })
                if distribute_type == "automatic":
                    context.update({
                        "distribute_method": distribute_method,
                        "vendor_selection": vendor_selection})
                vendor_id_obj_list.append(context)

    else:
        for vendor_id in vendor_id_data_list:
            context = {
                'program_id': program_id,
                'job_id': job_id,
                'distribute_type': distribute_type,
                'vendor_id': vendor_id,
            }

            if submission_limit:
                context.update({
                    "submission_limit": submission_limit
                })
            if distribute_type == "automatic":
                context.update({
                    "distribute_method": distribute_method,
                    "vendor_selection": vendor_selection})

            vendor_id_obj_list.append(context)
    return vendor_id_obj_list


def get_vendor_submitted_candidates(request, program_id, job_id, vendor_id):
    '''
    Returns  vendor submitted candidates list
    provided.
    '''
    # vendor_id = "52b42aee-4680-49b7-9897-db26be8e7354"
    url_format_dict = {
        "configurator_base_url": settings.VENDOR_ENDPOINT,
        "program_id": program_id,
        "job_id": job_id,
        "vendor_id": vendor_id
    }

    url = settings.GET_VENDOR_SUBMITTED_CANDIDATES.format(**url_format_dict)
    # url = "http://dev-awsnlb.simplifyvms.com:8003/configurator/programs/0159d8b1-00b7-428a-a5c4-884d3c9d4ac3/jobs/0608f708-375d-4bc9-9af8-b0e64fce065e/candidates?vendor_id=0608f708-375d-4bc9-9af8-b0e64fce065e"

    headers = {
        'Authorization': request.headers["Authorization"]
    }

    content_type = request.headers.get("Content-Type")
    user_agent = request.headers.get("User-Agent")

    if content_type:
        headers["Content-Type"] = content_type

    if user_agent:
        headers["User-Agent"] = user_agent

    try:
        # url = "http://dev-awsnlb.simplifyvms.com:8003/configurator/organizations/52b42aee-4680-49b7-9897-db26be8e7354"
        response = requests.get(
            url, headers=headers,
            timeout=(settings.CONNECTIVITY, settings.RESPONSE_TIMEOUT))
        response.raise_for_status()
    except requests.exceptions.HTTPError as error:
        settings.LOGGER.error(
            'error: could not get total count of submitted candidate from url {}  because of {}'.format(
                url, response.status_code))
        return {"total_records": 0}

    return response.json()
