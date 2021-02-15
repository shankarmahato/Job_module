from decouple import config
from django.conf import settings
from rest_framework import exceptions
from rest_framework.authentication import get_authorization_header, \
                                            SessionAuthentication
from rest_framework.permissions import BasePermission
from connectors.vms_profile_manager.protoc import profile_manager_pb2, profile_manager_pb2_grpc

# setup logging
import logging.config
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

        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None
        
        if len(auth) == 1 or len(auth) > 2:
            msg = _('Invalid token header.')
            raise exceptions.AuthenticationFailed(msg)
        
        try:
            token = auth[1].decode()
        except UnicodeError:
            msg = _('Invalid token header. Token string should not contain invalid characters.')
            raise exceptions.AuthenticationFailed(msg)
        
        return self.authenticate_credentials(token=token, 
                                                ua=request.META.get('HTTP_USER_AGENT', b'SYSTEM'))
    
    def authenticate_credentials(self, token, ua):
        data = (None, token)
        try:
            # validate JWT token from remote server
            stub = profile_manager_pb2_grpc.AuthenticationStub(settings.AUTH_GRPC_CHANNEL)
            token_req = profile_manager_pb2.TokenRequest(token='Bearer {}'.format(token), ua=ua)
            user_info = stub.validateToken(token_req)
            if user_info is not None:
                data = (user_info, token)
        except Exception as e:
            logger.error(e)
        
        return data

    def authenticate_header(self, request):
        return self.keyword



class IsAuthenticated(BasePermission):
    """
        check whether user is authenticated to perform current operation
    """
    def has_permission(self, request, view):
        if request.user is not None and \
            request.user.id is not None and \
            len(request.user.id)==24:
            return True
        else:
            return False
 

