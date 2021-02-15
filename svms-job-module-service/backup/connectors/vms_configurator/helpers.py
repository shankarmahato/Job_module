from django.apps import AppConfig
from django.conf import settings
from .protoc import configurator_pb2, configurator_pb2_grpc
import grpc

class ConfiguratorConfig(AppConfig):
	name = 'configurator'


class ProgramHandler():
	@staticmethod
	def getProgramInstance(request, program_id):

		# Connect gRPC channel: Configurator Manager
		channel = settings.PROGRAM_GRPC_CHANNEL
		
		stub = configurator_pb2_grpc.ProgramStub(channel)
		program_req = configurator_pb2.ProgramInfoRequest(program_id=str(program_id))
		program_info = stub.getProgramInfo(program_req)
		print(program_info)
		return program_info