from django.apps import AppConfig
from decouple import config
import json
from .protoc import logger_pb2, logger_pb2_grpc
import datetime


class LoggerConfig(AppConfig):
    name = 'logger'


class AuditLoghandler():
    @staticmethod
    def get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    @staticmethod
    def get_user_agent(request):
        return request.META.get('HTTP_USER_AGENT', 'SYSTEM')

    @staticmethod
    def saveAuditLog(request, source, user_id, program, action, record_type, record_ref, meta_data=None):
        ip = AuditLoghandler.get_client_ip(request)
        user_agent = AuditLoghandler.get_user_agent(request)

        if program is not None:
            program = program

        payload = {
            'program': program,
            'user': user_id,
            'source': source,
            'ip': ip,
            'user_agent': user_agent,
            'action': action,
            'record_type': record_type,
            'record_ref': record_ref,
            'meta_data': meta_data,
            'created_on': str(datetime.datetime.utcnow().timestamp())
        }

        # Connect gRPC channel: Auth Manager
        import grpc
        channel = grpc.insecure_channel(config('LOGGING_GRPC_ENDPOINT'))

        # validate JWT token from remote server
        stub = logger_pb2_grpc.LoggerStub(channel)
        audit_log_req = logger_pb2.AuditLogRequest(**payload)
        audit_log_info = stub.saveAuditLog(audit_log_req)
        print(audit_log_info)
        return audit_log_info
