from decouple import config
from django.conf import settings
from rest_framework import exceptions
from rest_framework.authentication import get_authorization_header, \
    SessionAuthentication
from rest_framework.permissions import BasePermission
import requests
import json
from collections import namedtuple
from simplify_job.cache import RedisCacheHandler
# setup logging
import logging.config
from connectors.vms_profile_manager.helpers import RemoteUserDataHandler
import hashlib 
logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger(__name__)


class RemoteJWTAuthentication(SessionAuthentication):
    """
    JWT token based authentication.

    Clients should authenticate by passing the token key in the "Authorization"
    HTTP header, prepended with the string "Bearer ".  For example:

        Authorization: Bearer <JWT_TOKEN_VALUE>
    """

    keyword = 'Bearer'

    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening

    """ 
    A custom token model may be used, but must have the following properties.

    * key -- The string identifying the token
    * user -- The user to which the token belongs
    """

    def authenticate(self, request):
        auth = get_authorization_header(request).split()
        if not auth:
            raise exceptions.AuthenticationFailed("Kindly provide the token")

        if len(auth) == 1 or len(auth) > 2:
            msg = "Invalid token header."
            raise exceptions.AuthenticationFailed(msg)

        try:
            token = auth[1].decode()
        except UnicodeError:
            msg = _(
                'Invalid token header. Token string should not contain invalid characters.')
            raise exceptions.AuthenticationFailed(msg)

        return self.authenticate_credentials(request=request,token=token,
                                             ua=request.META.get('HTTP_USER_AGENT', b'SYSTEM'))

    def authenticate_credentials(self, token, ua,request):
        data = (None, token)
        try:
            # validate JWT token from remote server
            # url = '{}/profile-manager/authentication/validate'.format(
            #      config('PROFILE_BASE_URL'))
            # url = settings.AUTH_VALIDATE.format(profile_base_url=settings.PROFILE_BASE_URL)
            # url = 'http://uat-wipro-nlb.simplifysandbox.net:8004/profile-manager/authentication/validate'
            # user_info_response = requests.get(url, headers={
            #     'Authorization': 'Bearer {}'.format(token),
            #     'user-agent': ua
            # })
            key =  settings.TOKEN_KEY.format(hashlib.md5(token.encode('utf-8')).hexdigest())
            user_info  = RedisCacheHandler.get(key)
            logger.info('Recieved Response from cache key: {}: data: {}'.format( key, user_info))

            if not user_info:
                logger.info('Unable to get cache data of key: {}: data: {}'.format( key, user_info))
                url = settings.AUTH_VALIDATE.format(profile_base_url=settings.PROFILE_BASE_URL)
                logger.info('Validate API Request {}'.format(url))
                user_info_response = requests.get(url, headers={
                'Authorization': 'Bearer {}'.format(token),
                'user-agent': ua
                })
                logger.info('Validate API Response {}'.format(user_info_response.status_code))
                if user_info_response.status_code != 200:
                    raise exceptions.AuthenticationFailed()
                else:
                    logger.info('Validate API data {}'.format(user_info_response.text))
                    user_data = user_info_response.text
                    user_info = json.loads(user_data)

            user_info = user_info['user']
            request.session['created_by'] = user_info['id']
            request.session['modified_by'] = user_info['id']

            keys_to_remove = [
                '_id'
                # 'provider',
                # 'educational_qualifications',
                # 'social_profiles',
                # 'email_addresses',
                # 'contact_numbers',
                # 'addresses'
            ]

            for key in keys_to_remove:
                user_info.pop(key)

            user_info = namedtuple("user", user_info.keys())(
                *user_info.values())
            if user_info is not None:
                data = (user_info, token)
                logger.info("Authenticated!!")
                return data
        except Exception as e:
            logger.error("Authentication Failed: {}".format(e))
            raise exceptions.AuthenticationFailed()

    def authenticate_header(self, request):
        return self.keyword


class IsAuthenticated(BasePermission):
    """
        check whether user is authenticated to perform current operation
    """

    def has_permission(self, request, view):
        if request.user is not None and \
                request.user.id is not None and \
                len(str(request.user.id)) == 36:
            return True
        else:
            return False
