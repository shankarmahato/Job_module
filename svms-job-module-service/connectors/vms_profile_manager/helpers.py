from django.apps import AppConfig
import requests
from decouple import config
from django.conf import settings
import json
from collections import namedtuple
import urllib.parse


# setup logging
import logging.config
logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger(__name__)


class RemoteUserDataHandler:
    profile_api = settings.PROFILE_API

    def __init__(self, token=None, user_agent=None):
        self.token = token
        self.user_agent = user_agent

    @staticmethod
    def get_user(user_id):
        cache_key = '_user_{}'.format(user_id)
        user_info = settings.TTLCACHE.get(cache_key)
        if user_info is None:
            try:
                # url = config('PROFILE_BASE_URL') + '/profile-manager/users/{user_id}'.format(user_id=user_id)
                url = settings.GET_USER.format(user_id=user_id)
                print(url)
                user_info_response = requests.get(url)
                user_info = user_info_response.json()
                user_info = user_info['user']
                print(user_info_response)
                # keys_to_remove = ['_id', 'provider', 'educational_qualifications', 'social_profiles', 'email_addresses', 'contact_numbers',
                #                   'addresses']

                # for key in keys_to_remove:
                if '_id' in user_info.keys():
                    user_info.pop('_id')
                user_info = namedtuple("UserInfoResponse", user_info.keys())(
                    *user_info.values())
                settings.TTLCACHE[cache_key] = user_info
                return user_info
            except Exception as e:
                logger.error(e)
                return None
        else:
            return user_info

    @staticmethod
    def get_user_by_email(email):
        cache_key = '_useremail_{}'.format(email)
        user_info = settings.TTLCACHE.get(cache_key)
        if user_info is None:
            # PROFILE_BASE_URL = config('PROFILE_BASE_URL')
            email = urllib.parse.quote(email)
            url = '{PROFILE_BASE_URL}/profile-manager/users?email={email}'.format(
                PROFILE_BASE_URL=config('PROFILE_BASE_URL'), email=email)
            user_info_response = requests.get(url)
            user_info = json.loads(user_info_response.text)
            if user_info['users'] and len(user_info['users']) > 0:
                user_info = user_info['users'][0]
                settings.TTLCACHE[cache_key] = user_info
            else:
                user_info = None
            return user_info
        else:
            return user_info

    def create_user(self, payload):
        # create user to remote server
        try:
            # TODO: Need to change user create API endpoint
            url = settings.CREATE_USER.format(profile_base_url=settings.PROFILE_BASE_URL)
            user_info_response = requests.post(url, json=payload)
            user_info = json.loads(user_info_response.text)
            if 'user' in user_info:
                user_info = user_info['user']
                user_resp = namedtuple("UserInfoResponse", user_info.keys())(
                    *user_info.values())
                return user_resp.id
            else:
                return None
        except Exception as e:
            logger.error(e)
            return None


    def update_user(self, payload, org_id, user_id):
        try:
            url = settings.UPDATE_USER.format(profile_base_url=settings.PROFILE_BASE_URL)
            user_info_response = requests.put(url, json=payload)
            user_info = json.loads(user_info_response.text)
            return user_info['member']['id']
        except Exception as e:
            logger.error(e)
            return None


    @staticmethod
    def get_org_member_list(org_id):
        # update user to remote server via gRPC
        try:
            url = RemoteUserDataHandler.profile_api+'organizations/{org_id}/members'.format(
                org_id=org_id)
            # user_info_response = requests.put(url, json=payload, headers={
            #                                   'Authorization': 'Bearer {token}'.format(token=self.token), 'user-agent': self.user_agent})
            user_info_response = requests.get(url)
            user_info = json.loads(user_info_response.text)
            if 'memberList' in user_info:
                user_info = user_info['memberList']
                return user_info
            else:
                return None
        except Exception as e:
            logger.error(e)
            return None

    @staticmethod
    def invite_user(org_id, payload):
        # invite user to remote server
        try:
            # TODO: Need to change user invite API endpoint
            url = '{PROFILE_BASE_URL}/profile-manager/organizations/{org_id}/members/invite/'.format(
                PROFILE_BASE_URL=config('PROFILE_BASE_URL'), org_id=org_id)
            user_info_response = requests.post(url, json=payload)
            user_info = json.loads(user_info_response.text)
            if 'member' in user_info:
                user_info = user_info['member']
                user_resp = namedtuple("UserInfoResponse", user_info.keys())(
                    *user_info.values())
                return user_resp.id
            else:
                return None
        except Exception as e:
            logger.error(e)
            return None

    @staticmethod
    def notification_email(user_email, subject, html_content):
        try:
            payload = {
                "template_id": 3,
                "reciever_email": [user_email],
                "subject": subject,
                "template_variables": html_content,
                "language": 1
            }

            r = requests.post(
                f"{config('NOTIFICATION_EMAIL_BASE_URL')}/api/notification/email",
                json = payload
            )

            if r.status_code == 202:
                return True
            else:
                return False

        except Exception as e:
            print(e)
            return None
