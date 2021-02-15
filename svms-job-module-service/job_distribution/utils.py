import requests
from django.conf import settings

from job.utils import get_token_user_agent, get_redis_data

logger = settings.LOGGER


def get_location_details(request, program_id, location_id):
    """
    get location details
    @param request:
    @type request:
    @param program_id:
    @type program_id:
    @param location_id:
    @type location_id:
    @return:
    @rtype:
    """
    token, ua = get_token_user_agent(request)
    is_api_hit_require = True
    work_location_details = {}
    try:
        url = settings.WORK_LOCATION.format(
            configurator_base_url=settings.CONFIGURATOR_BASE_URL,
            program_id=program_id, location_id=location_id)
        key = settings.WORK_LOCATION_KEY.format(program_id, location_id)

        status, cache_data = get_redis_data(key)

        if status:
            try:
                work_location_details = cache_data['work_location']
                is_api_hit_require = False
            except Exception as error:
                logger.error(
                    "Unable to read work_location: {},cache data for Program:{}".format(
                        location_id, error))

        if is_api_hit_require:
            logger.info("Sending request to configurator, url:{}".format(url))
            response = requests.get(url, headers={
                'Authorization': 'Bearer {}'.format(token),
                'user-agent': ua
            }, timeout=(settings.CONNECTIVITY, settings.RESPONSE_TIMEOUT))
            logger.info("Response from configurator: {}".format(
                response.status_code
            ))
            if response.status_code == 200:
                work_location_details = response.json()['work_location']

    except Exception as e:
        logger.error(
            "Unable to read work_location: {}, data for Program: {}".format(
                location_id, e))

    return work_location_details
