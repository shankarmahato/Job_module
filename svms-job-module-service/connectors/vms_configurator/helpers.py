from django.apps import AppConfig
from django.conf import settings
from .protoc import configurator_pb2, configurator_pb2_grpc
import requests
from decouple import config
# setup logging
import logging.config
logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger(__name__)


class ConfiguratorConfig(AppConfig):
	name = 'configurator'

CONFIGURATOR_BASE_URL = "http://qa-awsnlb.simplifyvms.com:8003"



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


class CandidateHandler:

	@staticmethod
	def get_candidate(candidate_id, token, ua):
		try:
			url = settings.GET_CANDIDATES.format(configurator_base_url=settings.CONFIGURATOR_BASE_URL, candidate_id=candidate_id)
			candidate_info_response = requests.get(url, headers={'Authorization': 'Bearer {}'.format(token), 'user-agent': ua})
			candidate_info = candidate_info_response.json()
			candidate_info = candidate_info['candidate']
			return candidate_info

		except Exception as e:
			logger.error(e)
			return None


class ProgramListHandler:

	@staticmethod
	def get_program(program_id, token, ua):
		try:
			url = settings.GET_PROGRAM.format(configurator_base_url=settings.CONFIGURATOR_BASE_URL, program_id=program_id)
			program_info_response = requests.get(url, headers={'Authorization': 'Bearer {}'.format(token),
																 'user-agent': ua})
			program_info = program_info_response.json()
			program_info = program_info['program']
			return program_info

		except Exception as e:
			logger.error(e)
			return None



class ConfiguratorOnboardingHandler:

	@staticmethod
	def get_checklist(program_id, checklist_id, token, ua):
		try:
			url = settings.GET_CHECKLIST.format(program_id=program_id, checklist_id=checklist_id)
			response = requests.get(
				url,
				headers = {
					'Authorization': 'Bearer {}'.format(token),
					'user-agent': ua
				}
			)
			info = response.json()
			return info['checklist']
		except Exception as e:
			logger.error(e)
			return None


class ConfiguratorRoleHandler:

	@staticmethod
	def get_role(program_id, role_id, token, ua):
		try:
			url = settings.GET_ROLE.format(configurator_base_url=settings.CONFIGURATOR_BASE_URL, program_id=program_id, role_id=role_id)
			response = requests.get(
				url,
				headers = {
					'Authorization': 'Bearer {}'.format(token),
					'user-agent': ua
				}
			)
			info = response.json()
			return info['roles']
		except Exception as e:
			logger.error(e)
			return None


class QualificationHandler:

	@staticmethod
	def get_qualification_type(program_id, qualification_type_id, token, ua):
		try:
			url = settings.GET_QUALIFICATION_TYPE.format(program_id=program_id, qualification_type_id=qualification_type_id)
			qualification_type_info_response = requests.get(url, headers={'Authorization': 'Bearer {}'.format(token), 'user-agent': ua})
			qualification_type_info = qualification_type_info_response.json()
			qualification_type_info = qualification_type_info['qualification_type']
			return qualification_type_info

		except Exception as e:
			logger.error(e)
			print(e)
			return None


	@staticmethod
	def get_qualification(program_id, qualification_type_id, qualification_id, token, ua):
		try:
			url = settings.GET_QUALIFICATION.format(program_id=program_id, qualification_type_id=qualification_type_id, qualification_id=qualification_id)
			qualification_info_response = requests.get(url, headers={'Authorization': 'Bearer {}'.format(token), 'user-agent': ua})
			qualification_info = qualification_info_response.json()
			qualification_info = qualification_info['qualification']
			return qualification_info

		except Exception as e:
			logger.error(e)
			print(e)
			return None
