from rest_framework.response import Response
from rest_framework import status
from job.models import Job
import re
import uuid


class ValidateHandeler:

    @staticmethod
    def is_valid_uuid(val):
        try:
            return uuid.UUID(str(val))
        except ValueError:
            return None
        
    @staticmethod
    def job_validator(job_id):
        if ValidateHandeler.is_valid_uuid(job_id) == None:
            return Response({
                'error': {
                    "ref": "INVALID_JOB_ID",
                    "message": "Job Id is not valid."
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        try:
            return Job.objects.get(uid=job_id, is_deleted=False)
        except Job.DoesNotExist:
            return Response({
                'error': {
                    "ref": "INVALID_JOB_ID",
                    "message": "Job does not exist !"
                }
            }, status=status.HTTP_404_NOT_FOUND)
