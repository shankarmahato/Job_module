from django.apps import AppConfig
import requests
from decouple import config
from django.conf import settings
from connectors.vms_profile_manager.protoc import profile_manager_pb2, profile_manager_pb2_grpc
import grpc
import json

# setup logging
import logging.config
logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger(__name__)

class RemoteUserDataHandler:
    def __init__(self, token=None, user_agent=None):
        self.token = token
        self.user_agent = user_agent

    @staticmethod
    def get_user(user_id):        
        cache_key = '_user_{}'.format(user_id)
        user_info = settings.TTLCACHE.get(cache_key)
        if user_info is None:
            try:
                stub = profile_manager_pb2_grpc.ProfileStub(settings.AUTH_GRPC_CHANNEL)
                user_info_req = profile_manager_pb2.UserInfoRequest(user_id=user_id)
                user_info = stub.getUserInfo(user_info_req)
                settings.TTLCACHE[cache_key] = user_info
                return user_info
            except Exception as e:
                logger.error(e)
                return None
        else:
            return user_info


    def create_user(self, payload):
        # create user to remote server via gRPC
        try:
            stub = users_pb2_grpc.ProfileStub(settings.AUTH_GRPC_CHANNEL)
            user_create_req = users_pb2.UserCreateRequest(**payload)
            user_resp = stub.createUser(user_create_req)
            return user_resp.id
        except grpc.RpcError as e:
            msg = json.loads(e.details())
            if e.code() == grpc.StatusCode.ALREADY_EXISTS:
                return msg.get('id')
            else:
                return None