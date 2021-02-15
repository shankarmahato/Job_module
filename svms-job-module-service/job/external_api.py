from django.conf import settings
from urllib.error import HTTPError
from .utils import (
    get_token_user_agent
)
from job.utils import get_redis_data
import requests
import time
logger = settings.LOGGER


class ConfiguratorService:

    def concurrent_response(self, request, urls, program_id, check_duplicate_urls):
        """
        Call the requests using process pool executor parallelly.
        """
        logger.info('Handling request: %s', request)

        if isinstance(request, dict):

            token = request.get("token")
            ua = request.get("ua", "SYSTEM")
            token = token.split()[-1]
        else:
            token, ua = get_token_user_agent(request)

        headers = {
            'Authorization': 'Bearer {}'.format(token),
            'user-agent': ua,
        }
        response_obj = []
        logger.info('Starting service')

        api_status_code = None
        check_urls = ["users", "hierarchy", "location_id"]
        other_urls = ["foundational_data","qualifications"]

        try:
            # Checking cache data, appending them in url list
            for url in urls:
                cache_status = False
                status_from_another_list = False
                if isinstance(url, dict):
                    url_link = url['url']
                    
                    if url['dict_key'] in check_urls:
                        list_key = str(url['id']["id1"])+"-"+url['dict_key']
                        if list_key in check_duplicate_urls:
                            data = check_duplicate_urls[list_key]
                            if 'content' in data:
                                content = data['content']
                                cache_status = True
                                cache_data = content
                                status_from_another_list = True
                                api_status_code = data['status_code']

                    if url['dict_key'] in other_urls:
                        list_key = str(url['id']["id1"])+"-"+str(url['id']["id2"])+"-"+url['dict_key']
                        if list_key in check_duplicate_urls:
                            data = check_duplicate_urls[list_key]
                            if 'content' in data:
                                content = data['content']
                                cache_status = True
                                cache_data = content
                                status_from_another_list = True
                                api_status_code = data['status_code']

                    # Get Cache Data
                    if not status_from_another_list:
                        if url['dict_key'] == "users":
                            key = settings.USERS_KEY.format(program_id, url['id']["id1"])
                            status, cache_data = get_redis_data(key)
                            if status:
                                cache_status = True
                                # cache_data = {"member": cache_data}

                        elif url['dict_key'] == "location_id":
                            key = settings.WORK_LOCATION_KEY.format(program_id, url['id']["id1"])
                            status, cache_data = get_redis_data(key)
                            if status:
                                cache_status = True
                                # cache_data = {"work_location": cache_data}
                        
                        elif url['dict_key'] == "hierarchy":
                            key = settings.HIERARCHY_KEY.format(program_id, url['id']["id1"])
                            status, cache_data = get_redis_data(key)
                            if status:
                                cache_status = True
                                # cache_data = {"hierarchy": cache_data}

                        elif url['dict_key'] == "qualifications":
                            key = settings.QUALIFICATION_KEY.format(program_id, url['id']["id1"], url['id']["id2"])
                            status, cache_data = get_redis_data(key)
                            if status:
                                cache_status = True

                        elif url['dict_key'] == "foundational_data":
                            key = settings.FOUNDATIONAL_KEY.format(program_id, url['id']["id1"], url['id']["id2"])
                            status, cache_data = get_redis_data(key)
                            if status:
                                cache_status = True

                    if cache_status:
                        if api_status_code:
                            get_status_code = api_status_code
                        else:
                            get_status_code = 200
                        context = {
                            'job_id': url['job_id'],
                            'dict_key': url['dict_key'],
                            'url': url['url'],
                            'id': url['id'],
                            'content': cache_data,
                            'status_code': get_status_code
                        }

                        if url['dict_key'] in check_urls:
                            list_key = str(url['id']["id1"])+"-"+url['dict_key']
                            if list_key in check_duplicate_urls:
                                data_check = check_duplicate_urls[list_key]
                                data_check["content"] = cache_data
                                data_check["status_code"] = get_status_code
                        
                        response_obj.append(context)
                    else:
                        if isinstance(url, dict):
                            url_link = url['url']
                            context = {
                                'job_id': url['job_id'],
                                'dict_key': url['dict_key'],
                                'url': url['url'],
                                'id': url['id']
                            }
                        else:
                            url_link = url
                            context = {
                                'url': url_link
                            }

                        try:
                            logger.info("Request URL {}".format(url_link[0]))
                            resp = requests.get(url_link[0], headers=headers, timeout=(settings.CONNECTIVITY,settings.RESPONSE_TIMEOUT))
                            res_status_code  = resp.status_code
                        
                        except Exception as error_request:
                            logger.info("error in requests, url: {}, error - {} ".format(url_link[0], error_request))
                            res_status_code = 500
                            res = {}


                        try:
                            if res_status_code in [500, 404, 400]:
                                res = {}
                            else:
                                res = resp.json()
                                logger.info("Response - {}".format(res))

                            if url['dict_key'] in check_urls:
                                list_key = str(url['id']["id1"])+"-"+url['dict_key']
                                if list_key in check_duplicate_urls:
                                    data_check = check_duplicate_urls[list_key]
                                    data_check["content"] = res
                                    data_check["status_code"] = res_status_code

                        except Exception as e:
                            logger.error(
                                "Error in concurrent response - {}".format(e))

                        else:
                            context.update({
                                'content': res,
                                'status_code': res_status_code

                            })
                        response_obj.append(context)
                else:
                    continue
            logger.info('Received response: %s', response_obj)
            return response_obj
        except Exception as error:
            logger.error('Error Occurred: %s', error)