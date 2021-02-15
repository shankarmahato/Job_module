import requests
import json
import logging
import datetime
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import LimitOffsetPagination
from connectors.vms_profile_manager.auth import IsAuthenticated, RemoteJWTAuthentication
from job.serializers import *
from job.models import JobConfiguration, Job, JobCustom, TalentNeuron
from drf_yasg.utils import swagger_auto_schema
from job.swagger_constants import (
    GET_JOB,
    POST_JOB,
    PUT_JOB,
    DELETE_JOB,
    POST_JOB_CONFIGRATION,
    POST_COPYJOB,
    PUT_JobApproval,
    GET_RECENTJOB,
    GET_DRAFTJOB,
    GET_POPULARJOB,
    GET_JOBTEMPLATE,
    GET_JOBQUALIFICATION,
    GET_UNIQUETEMPLATE
)
from job.update_response import update_response_data
from job.utils import (
    get_filter_data,
    stomp_connectivity,
    PaginationHandlerMixin,
    post_candidate,
    organization_id,
    updated_custom_columns,
    retrieve_custom_columns,
    url_list,
    validate_approval,
    get_program_name,
    submit_candidate,
    notification_email,
    update_checklist_onboarding,
    validate_checklist_data,
    check_duplicate_url,
    job_from_template,
    job_from_catalog,
    get_uid,
    add_job_id
)
from rest_framework import viewsets
from django.db.models import Q
from django.forms import model_to_dict
from django.core.paginator import Paginator
from job.pagination import JobsPagination
from .job_vms import vms_dashboard
from .utils import read_configurator_data
from django.conf import settings
from .external_api import ConfiguratorService
from django.core import cache
from job.retrieve_job import retrieve_jobs, get_candidate
from simplify_job.cache import RedisCacheHandler
import uuid
from rest_framework import exceptions
from .utils import get_token_user_agent
import copy

logger = settings.LOGGER


def decide_on_queryset(view_name, program_id, vendor):
    logger.info('Program ID: %s', program_id)
    if vendor:
        job_queryset = Job.objects.filter(is_delete=False, program_id=program_id, id__in=vendor)
    else:
        job_queryset = Job.objects.filter(is_delete=False, program_id=program_id)

    context = {
        'job': job_queryset,
        'recent_job': job_queryset,
        'draft_job': job_queryset.filter(submit_type="Draft"),
        'popular_job': job_queryset,
        'job_template': job_queryset.filter(is_template=True)
    }

    return context[view_name]


def job_returned_queryset(view_name, request, program_id, uid=None):
    cache_flag = False
    logger.info('Handling request: %s', request)
    # Program Name
    program_obj = get_program_name(request, program_id)
    logger.debug('Program Object: %s..', program_obj)
    status = True
    message = None

    # Invalid program_id
    if program_obj == None:
        queryset = []
    else:
        # Get Vendors
        vendor = organization_id(request, program_id, request.session['created_by'])
        logger.info("Vendor for {} is {}".format(view_name, vendor))
        queryset = decide_on_queryset(view_name, program_id, vendor)
        # To get Single Jobs
        if uid:
            # Get Cache details
            cache_key = settings.REDIS_JOB_KEY.format(program_id=program_id, job_uid=uid)
            cache_data = RedisCacheHandler.get(cache_key)
            if cache_data:
                cache_flag = True
                logger.info('Retrieving Cache Object: %s..', cache_data)
                queryset = cache_data
            else:
                queryset = queryset.filter(uid=uid)
        elif request.GET:
            try:
                query = request.GET.get("q")
                if query:
                    q_object = Q()
                    q_object.add((
                        Q(category__category_name__icontains=query) |
                        Q(template_name__icontains=query) |
                        Q(title__title__icontains=query) |
                        Q(description__icontains=query)
                    ), Q.OR)
                    queryset = queryset.filter(q_object).distinct()

                and_condition = get_filter_data(request)
                queryset = queryset.filter(and_condition)

                if "order_by" in request.GET:
                    order_by = request.GET["order_by"]
                    if order_by == "desc":
                        queryset = queryset.order_by('-title')

                    try:
                        field_name = request.GET['key']
                        if field_name:
                            if order_by=="desc":
                                queryset = queryset.order_by('-'+field_name)
                            else:
                                queryset = queryset.order_by(field_name)
                    except Exception as e:
                        logger.error("order by issue -- {}".format(e))    
            except Exception as error:
                logger.error("error -- {}".format(error)) 
                status = False
                message = {"error": {"ref": "ERROR_OCCURRED", "message": error}}

    return queryset, program_obj, cache_flag, message, status


def job_response(request, program_id, queryset, serializer_obj, program_obj, cache_status, set_cache, uid=None):
    logger.info('Handling request: %s', request)

    if cache_status:
        all_job_data = queryset
    else:
        data = retrieve_jobs(program_id, serializer_obj, request, uid)
        parallel_request_data = ConfiguratorService().concurrent_response(request, url_list, program_id,
                                                                          check_duplicate_url)
        url_list.clear()
        check_duplicate_url.clear()
        all_job_data = update_response_data(data, parallel_request_data, uid)
        if uid and set_cache:
            cache_key = settings.REDIS_JOB_KEY.format(program_id=program_id, job_uid=uid)
            logger.info('setting cache data of Job id: %s', uid)
            RedisCacheHandler.set(cache_key, all_job_data)

    if uid:
        context = {
            "program_id": program_id,
            "program_name": program_obj,
            "data": all_job_data
        }
    elif all_job_data:
        context = {
            "total_count": len(queryset),
            "items_per_page": len(all_job_data),
            "program_id": program_id,
            "program_name": program_obj,
            "data": all_job_data
        }
    else:
        context = {
            "total_count": len(queryset),
            "items_per_page": len(all_job_data),
            "data": all_job_data
        }

    return context, True


class CopyJob(APIView, PaginationHandlerMixin):
    authentication_classes = [RemoteJWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = JobsPagination

    @swagger_auto_schema(
        operation_description=POST_COPYJOB,
        # request_body=JobTitleSerializer,
    )
    def post(self, request, program_id, uid):

        # Program Name
        program_obj = get_program_name(request, program_id)
        logger.debug('Program Object: %s..', program_obj)
        if program_obj:
            try:
                # Create copy of job object
                status_approval = False
                created_by = request.session['created_by']
                modified_by = request.session['modified_by']
                try:
                    job = Job.objects.get(uid=uid)
                    old_job = copy.deepcopy(job)
                    job.pk = None
                    job.uid = uuid.uuid4()
                    job.status = "pending_approval"
                    job.created_by = created_by
                    job.modified_by = modified_by
                    job.source = 'CopyJob'
                    job.source_id = old_job.uid
                    job.save()

                    # Foundational Data 
                    check_job_obj = FoundationQualificationData.objects.filter(job=old_job)
                    if check_job_obj:
                        for each_data in check_job_obj:
                            old_foundational_data = copy.deepcopy(each_data)
                            each_data.pk = None
                            each_data.uid = uuid.uuid4()
                            each_data.job = job
                            each_data.save()
                    else:
                        logger.info("No Foundational Data found of Job -- {} ".format(old_job.uid))

                except Exception as e:
                    logger.error(e)
                    return Response({'error': {"message": "Job doesnot exists", "code": status.HTTP_404_NOT_FOUND, }
                                     }, status=status.HTTP_404_NOT_FOUND)

                if job.submit_type == "Submit" and job.status == "pending_approval":
                    if uid:
                        job_detail_status = True
                    else:
                        job_detail_status = False

                    queryset_job = Job.objects.filter(id=job.id)
                    queryset, program_obj, cache_flag = job_returned_queryset('job', request, program_id, job.uid)
                    data, job_status = job_response(request, program_id, queryset_job, queryset_job, program_obj,
                                                    cache_flag, False, job.uid)

                    if job_status:
                        # Approval Workflow
                        stomp_connectivity(data["data"], program_id)
                        # Notification for Job Creation
                        notification_email(data["data"], program_id)
                        # vms_dashboard integration
                        vms_dashboard(data["data"])
                        status_approval = True
                    else:
                        status_approval = False

                    logger.info(
                        " Response: Job {} Approval/Notification Status {}".format(job.id, status_approval))
                logger.info(" Response: Job {} saved successfully".format(job.title))
                return Response({"job": {"id": job.uid}, 'status': status.HTTP_201_CREATED},
                                status=status.HTTP_201_CREATED)

            except Exception as e:
                logger.error(e)
                return Response({'error': {"message": str(e), "code": status.HTTP_404_NOT_FOUND, }
                                 }, status=status.HTTP_404_NOT_FOUND)
        else:
            logger.error("Invalid Program Id - {}".format(program_id))
            return Response(
                {'error': {"ref": "INVALID PROGRAM_ID", "message": "Invalid Program Id - {}".format(program_id)}
                 }, status=status.HTTP_404_NOT_FOUND)


class JobView(APIView, PaginationHandlerMixin):
    """
    This view is used to list all the job and create the job.
    """
    authentication_classes = [RemoteJWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = JobsPagination

    def paginate_queryset(self, queryset):
        # why drf default pagination is not used
        if self.paginator is None:
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self)

    @swagger_auto_schema(
        operation_description=GET_JOB,
        # request_body=JobTitleSerializer,
    )
    def get(self, request, program_id=None, uid=None):
        """
        Define a list of job, dynamic filter filter and pagination

        :param request:
        :type request:
        :param uid:
        :type uid:
        :return:
        :rtype:
        Note: We will get program id then get config id then use,,To Do
        """
        logger.info(
            "Job View >> get >> request: {}".format(request.GET))
        queryset, program_obj, cache_flag, error_message, error_status = job_returned_queryset('job', request, program_id, uid)

        if error_status:
            if uid:
                jobs = queryset
            else:
                jobs = self.paginate_queryset(queryset)

            response_data, status_job = job_response(
                request,
                program_id,
                queryset,
                jobs,
                program_obj,
                cache_flag,
                True,  
                uid
            )
            logger.info('Response Data: %s', response_data)
            if status_job:
                return Response(response_data)
            else:
                return Response(error_message, status.HTTP_404_NOT_FOUND)
        else:
            return Response(error_message, status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description=POST_JOB,
        request_body=JobSerializer,
    )
    def post(self, request, program_id=None):
        """
        Create jobs with system and custom fields

        :param request:
        :type request:
        :return:
        :rtype:
        """
        status_approval = False
        logger.info(
            "JOBViewSet >> post >> request: {}".format(
                request))
        # Checking for valid program id
        program_obj = get_program_name(request, program_id)
        logger.debug('Program Object: %s..', program_obj)
        if program_obj:
            created_by = request.session['created_by']
            modified_by = request.session['modified_by']
            try:
                job = request.data
                conf_status, job, conf_custom_status = read_configurator_data(job)
                if not conf_status:
                    return Response({'error': {"ref": "ERROR OCCURRED",
                                               "message": job}
                                     }, status=status.HTTP_400_BAD_REQUEST)

                logger.info(
                    job.update({"created_by": created_by, "modified_by": modified_by}))

                logger.info(
                    "JOBViewSet >> post >> request: {}".format(request.data))
                job["program_id"] = program_id

                job, status_job, job_msg = get_uid(job)
                if not status_job:
                    return Response({'error': {"ref": "ERROR_OCCURED", "message": "Kindly provide valid uid - {}".format(job_msg)}
                                }, status=status.HTTP_400_BAD_REQUEST)


                if 'catalog' in job:
                    job, catalog_status, msg = job_from_catalog(job)
                    if not catalog_status:
                        return Response({'error': {"ref": "ERROR_OCCURED", "message": "Error in Catalog ID - {}".format(msg)}
                                }, status=status.HTTP_400_BAD_REQUEST)


                if 'template' in job:
                    job, template_status, msg = job_from_template(job)
                    if not template_status:
                        return Response({'error': {"ref": "ERROR_OCCURED", "message": "Error in Template ID - {}".format(msg)}
                                }, status=status.HTTP_400_BAD_REQUEST)                        

                if 'is_template' in job:
                    if job['is_template']:
                        if not 'template_name' in job:
                            return Response({'error': {"ref": "ERROR_OCCURED", "message": "Template Name is required"}
                                             }, status=status.HTTP_400_BAD_REQUEST)

                        if not 'checklist' in job:
                            return Response({'error': {"ref": "ERROR_OCCURED", "message": "Checklist is required"}
                                             }, status=status.HTTP_400_BAD_REQUEST)

                        checklist_status, msg = validate_checklist_data(job['checklist'], request, program_id)
                        if not checklist_status:
                            return Response({'error': {"ref": "ERROR_OCCURED", "message": msg}
                                             }, status=status.HTTP_400_BAD_REQUEST)

                        job_serializer = JobTemplateSerializer(data=job)

                    else:

                        job_serializer = JobSerializer(data=job)
                else:
                    job_serializer = JobSerializer(data=job)

                if job_serializer.is_valid(raise_exception=True):
                    job_saved = job_serializer.save()

                    # function to create unique Job ID (Program specific)
                    job_id_flag, msg = add_job_id(job_saved, program_obj)
                    if job_id_flag:
                        return Response({'error': {"ref": "ERROR_OCCURRED", "message": "Error in Job Creation - {}".format(msg)}
                                }, status=status.HTTP_400_BAD_REQUEST)
                    
                    job['job'] = job_saved.id
                    # add foundational and qualification json
                    if job['foundational_data']:
                        for qualification in job['foundational_data']:
                            qid = qualification["foundational_data_type_id"]
                            for qualification_dict in qualification['values']:
                                insert_foundational = FoundationQualificationData.objects.create(job=job_saved,
                                                                                                 program_id=program_id,
                                                                                                 entity_id=qid,
                                                                                                 entity_name="foundational",
                                                                                                 entity_key=
                                                                                                 qualification_dict[
                                                                                                     'id'])
                    if job['qualifications']:
                        for qualification in job['qualifications']:
                            qtype = qualification["qualification_type"]
                            qid = qualification["qualification_type_id"]
                            for qualification_dict in qualification['values']:
                                insert_qualification = FoundationQualificationData.objects.create(job=job_saved,
                                                                                                  program_id=program_id,
                                                                                                  entity_type=qtype,
                                                                                                  entity_id=qid,
                                                                                                  entity_name="qualification",
                                                                                                  entity_key=
                                                                                                  qualification_dict[
                                                                                                      'id'],
                                                                                                  entity_value=
                                                                                                  qualification_dict[
                                                                                                      'level'],
                                                                                                  entity_is_active=
                                                                                                  qualification_dict[
                                                                                                      'is_active'])

                    if "checklist" in job:
                        checklist_data = job["checklist"]
                        if isinstance(checklist_data, dict):
                            update_checklist_onboarding(checklist_data, request, program_id,job_saved.uid)

                if conf_custom_status:
                    serializer = CustomSerializer(data=job)
                    if serializer.is_valid(raise_exception=True):
                        serializer.save()

                if job['submit_type'] == "Submit" and job["status"] == "pending_approval":
                    # Candidate Integration
                    if job["candidates"]:
                        self.candidate_data(job_saved.uid, program_id, request)
                        logger.info(" Response: Candidate(s) created w.r.t Job {}".format(job_saved.uid))

                    queryset_job = Job.objects.filter(id=job_saved.id)
                    queryset, program_obj, cache_flag, error_message, error_status = job_returned_queryset('job', request, program_id, job_saved.uid)

                    if error_status:

                        data, job_status = job_response(request, program_id, queryset_job, queryset_job, program_obj, cache_flag, False, job_saved.uid)

                        if job_status:

                            # Approval Workflow
                            stomp_connectivity(data["data"], program_id)

                            # Notification for Job Creation
                            notification_email(data["data"], program_id)
                            # vms_dashboard integration
                            vms_dashboard(data["data"])
                            status_approval = True
                        else:
                            status_approval = False

                        logger.info(
                            " Response: Job {} Approval/Notification Status {}".format(job_saved.id, status_approval))
                        logger.info(" Response: Job {} saved successfully".format(job_saved.title))
                        return Response({"job": {"id": job_saved.uid}, 'status': status.HTTP_201_CREATED})
                    else:
                        return Response( error_message , status.HTTP_400_BAD_REQUEST)


            except Exception as e:
                logger.error(e)
                return Response({'error': {"ref": "ERROR_OCCURRED", "message": "Error in Job Creation - {}".format(e)}
                                 }, status=status.HTTP_400_BAD_REQUEST)

        else:
            logger.error("Invalid Program Id - {}".format(program_id))
            return Response(
                {'error': {"ref": "INVALID PROGRAM_ID", "message": "Invalid Program Id - {}".format(program_id)}
                 }, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description=PUT_JOB,
        request_body=CustomSerializer,
    )
    def put(self, request, uid, program_id=None):
        """
        update job data based on the given uid

        :param request:
        :type request:
        :param uid:
        :type uid:
        :return:
        :rtype:

        """
        # Checking for valid program id
        program_obj = get_program_name(request, program_id)
        logger.debug('Program Object: %s..', program_obj)

        if program_obj:
            modified_by = request.session['modified_by']
            job = request.data
            if not job:
                return Response({'error': {"ref": "ERROR_OCCURRED", "message": "Kindly provide the data"}}, 
                status.HTTP_400_BAD_REQUEST)

            logger.info(
                "JOBViewSet >> put >> request: {}".format(request.data))
            job.update({"modified_by": modified_by})
            settings.LOGGER.info(
                "JOBViewSet >> put >> request: {}".format(request.data))
            saved_job = get_object_or_404(Job.objects.all(), uid=uid, is_delete=False)
            cache_key = settings.REDIS_JOB_KEY.format(program_id=program_id, job_uid=uid)
            cache_data = RedisCacheHandler.purge(cache_key)
            job = retrieve_custom_columns(job)

            # After edit, job status will be pending for approval
            job["status"] = "pending_approval"

            job_serializer = JobSerializer(instance=saved_job, data=job, partial=True)
            try:

                if job_serializer.is_valid(raise_exception=True):
                    job_saved_data = job_serializer.save()
                    check_job_obj = FoundationQualificationData.objects.filter(job=job_saved_data)
                    if 'foundational_data' in job:
                        for foundational in job['foundational_data']:
                            qid = foundational["foundational_data_type_id"]
                            for foundational_dict in foundational['values']:
                                if not check_job_obj:
                                    insert_foundational = FoundationQualificationData.objects.create(job=job_saved_data,
                                                                                                     program_id=program_id,
                                                                                                     entity_id=qid,
                                                                                                     entity_name="foundational",
                                                                                                     entity_key=
                                                                                                     foundational_dict[
                                                                                                         'id'])
                                    if insert_foundational:
                                        logger.info("Foundational data Created")
                                else:
                                    update_foundational = FoundationQualificationData.objects.filter(job=job_saved_data).update(
                                                                                                program_id=program_id,
                                                                                                entity_id=qid,
                                                                                                entity_name="foundational",
                                                                                                entity_key=
                                                                                                foundational_dict['id'])
                                    if update_foundational:
                                        logger.info("Foundational data Updated")
                    if 'qualifications' in job:
                        for qualification in job['qualifications']:
                            qtype = qualification["qualification_type"]
                            qid = qualification["qualification_type_id"]
                            for qualification_dict in qualification['values']:
                                if not check_job_obj:
                                    create_qualification = FoundationQualificationData.objects.create(job=job_saved_data,
                                                                                             program_id=program_id,
                                                                                             entity_type=qtype,
                                                                                             entity_id=qid,
                                                                                             entity_name="qualification",
                                                                                             entity_key=qualification_dict['id'],
                                                                                             entity_value=qualification_dict['level'],
                                                                                             entity_is_active=qualification_dict['is_active'])

                                    if create_qualification:
                                        logger.info("Qualification Created")
                                else:
                                    update_qualification = FoundationQualificationData.objects.filter(job=job_saved_data).update(
                                                                                                program_id=program_id,
                                                                                                entity_type=qtype,
                                                                                                entity_id=qid,
                                                                                                entity_name="qualification",
                                                                                                entity_key=qualification_dict['id'],
                                                                                                entity_value=qualification_dict['level'],
                                                                                                entity_is_active=qualification_dict['is_active'])
                                    if update_qualification:
                                        logger.info("Qualification updated")
                    try:
                        custom_saved_job = get_object_or_404(JobCustom.objects.all(), job__id=job_saved_data.id,
                                                             is_delete=False)
                        if custom_saved_job:
                            serializer = CustomSerializer(instance=custom_saved_job, data=job, partial=True)
                            if serializer.is_valid(raise_exception=True):
                                job_saved = serializer.save()
                    except Exception as e:
                        logger.error('Error Occurred: %s', e)
                        pass

                    # GET CACHE KEY, then PURGE IT
                    cache_key = settings.REDIS_JOB_KEY.format(program_id=program_id, job_uid=uid)
                    logger.info('getting cache data of Job id: %s', uid)
                    cache_data = RedisCacheHandler.get(cache_key)
                    if cache_data:
                        RedisCacheHandler.purge(cache_key)

                    data = []
                    queryset_job = Job.objects.filter(id=job_saved_data.id)
                    queryset, program_obj, cache_flag, error_message, error_status = job_returned_queryset('job', request, program_id, job_saved_data.uid)
                    
                    if error_status:
                        data, job_status = job_response(request, program_id, queryset_job, queryset_job, program_obj, False, False, job_saved_data.uid)
                        # check_for_approval_status = validate_approval(job)
                        # if check_for_approval_status:
                        logger.info(
                                "JOBViewSet >> put >> Sending task to approval: {}".format(data))
                        # Approval Workflow for PUT Request
                        stomp_connectivity(data["data"], program_id)
                        logger.info(
                            "JOBViewSet >> put >> response: {}".format(job_saved_data.id))
                        logger.info(" Response: Job updated successfully")
                        return Response({"data": data}, status=status.HTTP_200_OK)
                    else:
                        return Response(error_message, status=status.HTTP_400_BAD_REQUEST)

            except Exception as e:
                logger.error('Error Occurred: %s', e)
                return Response({'error': {"ref": "ERROR_OCCURRED", "message": "Job not updated, {}".format(e)}
                                 }, status=status.HTTP_400_BAD_REQUEST)

        else:
            logger.error("Invalid Program Id - {}".format(program_id))
            return Response(
                {'error': {"ref": "INVALID PROGRAM_ID", "message": "Invalid Program Id - {}".format(program_id)}
                 }, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description=DELETE_JOB,
        # request_body=CustomSerializer,
    )
    def delete(self, request, uid, program_id=None):
        """
        delete job data based on the given uid

        :param request:
        :type request:
        :param uid:
        :type uid:
        :return:
        :rtype:

        """
        logger.info(
            "JOBViewSet >> delete >> request: {}".format(uid))
        try:
            check_template_in_job = Job.objects.filter(template__uid=uid,is_delete=False,program_id=program_id)
            if check_template_in_job:
                logger.info("Template used in job so it can't delete")
                return Response({"message":"Template used in job so it can't delete"},status=status.HTTP_200_OK)
            else:
                saved_job = Job.objects.filter(uid=uid, program_id=program_id, is_delete=False).update(is_delete=True)
                custom_job = JobCustom.objects.filter(job__uid=uid).update(is_delete=True)
                logger.info(
                    "JOBViewSet >> delete >> response: {}".format(custom_job))
                if saved_job:
                    cache_key = settings.REDIS_JOB_KEY.format(program_id=program_id, job_uid=uid)
                    cache_data = RedisCacheHandler.purge(cache_key)
                    return Response({"job": {"uid": uid}}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': {"ref": "JOB_ID_NOT_FOUND", "message": "Job id not found"}
                                     }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(e)
            return Response({'error': {"ref": "JOB_ID_NOT_FOUND", "message": "Job id not found"}
                             }, status=status.HTTP_400_BAD_REQUEST)


    def candidate_data(self, job_id, program_id, request):
        logger.info('Request: %s', request)

        payload = post_candidate(self, request)

        submission_status = submit_candidate(request, payload, job_id, program_id)

        return submission_status


class JobApprovalView(APIView):
    # authentication_classes = [RemoteJWTAuthentication]
    # permission_classes = [IsAuthenticated]
    pagination_class = LimitOffsetPagination

    @swagger_auto_schema(
        operation_description=PUT_JobApproval,
        request_body=JobSerializer,
    )
    def put(self, request, program_id, pk):
        """
        update job data based on the given pk

        :param request:
        :type request:
        :param pk:
        :type pk:
        :return:
        :rtype:

        """

        job = request.data
        settings.LOGGER.info(
            "JobApprovalViewSet >> put >> request: {}".format(request.data))
        saved_job = get_object_or_404(Job.objects.all(), pk=pk, is_delete=False)

        if job['status'] == "approved":
            job['status'] = "release_job"
        elif job['status'] == "rejected":
            job['status'] = "reject_job"
        if job['reason_1']:
            job['note_for_approver'] = job['reason_1']

        job_serializer = JobSerializer(instance=saved_job, data=job, partial=True)

        try:
            if job_serializer.is_valid(raise_exception=True):
                job_saved = job_serializer.save()
                logger.info(" Response: Job updated successfully")
                logger.info(
                    "JobApprovalViewSet >> put >> response: {}".format(job_saved.id))
                return Response({"job": {"id": job_saved.id}}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(e)
            error_list = []
            for key, value in job_serializer.errors.items():
                error_dict = {}
                error_dict['message'] = value[0]
                error_dict['field'] = key
                error_dict['type'] = "InputInvalid"
                error_list.append(error_dict)
            return Response({'error': {"message": "Job not updated", "code": status.HTTP_400_BAD_REQUEST,
                                       "errors": error_list}
                             }, status=status.HTTP_400_BAD_REQUEST)


class RecentJob(APIView, PaginationHandlerMixin):
    """Recent jobs"""
    authentication_classes = [RemoteJWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = JobsPagination

    def paginate_queryset(self, queryset):

        if self.paginator is None:
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self)

    @swagger_auto_schema(
        operation_description=GET_RECENTJOB,
        # request_body=JobSerializer,
    )
    def get(self, request, program_id, uid=None):
        logger.info(
            "RecentJob >> get >> request: {}".format(request.GET))

        job_queryset, program_obj, cache_flag, error_message, error_status = job_returned_queryset('recent_job', request, program_id, uid)

        if error_status:
            if uid:
                jobs = job_queryset
            else:
                jobs = self.paginate_queryset(job_queryset)
        

            response_data, status_job = job_response(
                request,
                program_id,
                job_queryset,
                jobs,
                program_obj,
                cache_flag, 
                True,
                uid
            )
            logger.info('Response Data: %s', response_data)
            if status_job:
                return Response(response_data)
            else:
                return Response(response_data, status.HTTP_404_NOT_FOUND)
        else:
            return Response(error_message, status.HTTP_400_BAD_REQUEST)


class DraftJob(APIView, PaginationHandlerMixin):
    """ Draft jobs"""
    authentication_classes = [RemoteJWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = JobsPagination

    def paginate_queryset(self, queryset):

        if self.paginator is None:
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self)

    @swagger_auto_schema(
        operation_description=GET_DRAFTJOB,
        # request_body=JobSerializer,
    )
    def get(self, request, program_id=None, uid=None):
        logger.info(
            "DraftJob >> get >> request: {}".format(request.GET))

        job_queryset, program_obj, cache_flag, error_message, error_status = job_returned_queryset('draft_job', request, program_id, uid)


        if error_status:
            if uid:
                jobs = job_queryset
            else:
                jobs = self.paginate_queryset(job_queryset)


            response_data, status_job = job_response(
                request,
                program_id,
                job_queryset,
                jobs,
                program_obj,
                cache_flag,
                True,
                uid
            )
            logger.info('Response Data: %s', response_data)

            if status_job:
                return Response(response_data)
            else:
                return Response(response_data, status.HTTP_404_NOT_FOUND)
        else:
            return Response(error_message, status.HTTP_400_BAD_REQUEST)



class PopularJob(APIView, PaginationHandlerMixin):
    """Popular jobs"""
    authentication_classes = [RemoteJWTAuthentication]
    permission_classes = [IsAuthenticated]
    # pagination_class = LimitOffsetPagination
    pagination_class = JobsPagination

    def paginate_queryset(self, queryset):
        if self.paginator is None:
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self)

    @swagger_auto_schema(
        operation_description=GET_POPULARJOB,
        # request_body=JobSerializer,
    )
    def get(self, request, program_id, uid=None):
        logger.info(
            "PopularJob >> get >> request: {}".format(request.GET))

        job_queryset, program_obj, cache_flag, error_message, error_status = job_returned_queryset('popular_job', request, program_id, uid)
        
        if error_status:
            if uid:
                jobs = job_queryset
            else:
                jobs = self.paginate_queryset(job_queryset)

            response_data, status_job = job_response(
                request,
                program_id,
                job_queryset,
                jobs,
                program_obj,
                cache_flag,
                True,
                uid
            )

            if status_job:
                return Response(response_data)
            else:
                return Response(response_data, status.HTTP_404_NOT_FOUND)
        else:
            return Response(error_message, status.HTTP_400_BAD_REQUEST)



class JobTemplateView(APIView, PaginationHandlerMixin):
    """Popular jobs"""
    authentication_classes = [RemoteJWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = JobsPagination

    def paginate_queryset(self, queryset):
        if self.paginator is None:
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self)

    @swagger_auto_schema(
        operation_description=GET_JOBTEMPLATE,
        # request_body=JobSerializer,
    )
    def get(self, request, program_id, uid=None):
        logger.info(
            "JobTemplateView >> get >> request: {}".format(request.GET))
        job_queryset, program_obj, cache_flag, error_message, error_status = job_returned_queryset('job_template', request, program_id, uid)
        
        if error_status:
            if uid:
                jobs = job_queryset
            else:
                jobs = self.paginate_queryset(job_queryset)

            response_data, status_job = job_response(
                request,
                program_id,
                job_queryset,
                jobs,
                program_obj,
                cache_flag,
                True,
                uid
            )
            logger.info('Response Data: %s', response_data)
            if status_job:
                return Response(response_data)
            else:
                return Response(response_data, status.HTTP_404_NOT_FOUND)
        else:
            return Response(error_message, status.HTTP_400_BAD_REQUEST)


class TalentNeuronView(viewsets.ModelViewSet):
    authentication_classes = [RemoteJWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = LimitOffsetPagination
    serializer_class = TalentNeuronSerializer

    def get_queryset(self):
        try:
            queryset = TalentNeuron.objects.all()
            ratecard_id = self.request.query_params.get('ratecard_id', None)
            if ratecard_id is not None:
                queryset = queryset.filter(rate_card_id=ratecard_id)
            return queryset
        except Exception as e:
            logger.error(e)
            return Response({"error": {"message": "{}".format(e), "code": status.HTTP_400_BAD_REQUEST}},
                            status.HTTP_400_BAD_REQUEST)


class UniqueTemplateName(APIView):
    """get unique template name"""
    authentication_classes = [RemoteJWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description=GET_UNIQUETEMPLATE,
        # request_body=JobSerializer,
    )
    def get(self, request, program_id):
        template_name = request.GET.get("template_name", None)
        try:
            check_name = Job.objects.filter(is_template=True, template_name=template_name, is_delete=False,
                                            program_id=program_id)
            if check_name:
                return Response({"error": {"message": "Template name is already exist", "code": 0}}, status.HTTP_200_OK)
            else:
                return Response({"error": {"message": "Template name is not exist", "code": 1}}, status.HTTP_200_OK)

        except Exception as e:
            logger.error(e)
            return Response({"error": {"message": "{}".format(e), "code": status.HTTP_400_BAD_REQUEST}},
                            status=status.HTTP_400_BAD_REQUEST)
