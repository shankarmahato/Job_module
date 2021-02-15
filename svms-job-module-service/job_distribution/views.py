import datetime

from django.conf import settings
from django.db.models import Q
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, viewsets, status
from rest_framework.response import Response

from connectors.vms_profile_manager.auth import IsAuthenticated, \
    RemoteJWTAuthentication
from job.models import Job
from job_distribution.config import (
    map_distribute_type,
    get_vendors,
    get_vendors_based_on_group_id,
    map_vendor_dict
)
from .models import VendorJobMapping, ScheduleJobVendorMapping
from .serializers import VendorJobMappingSerializer, \
    VendorJobMappingSerializerv2, OptInOptOutSerializer, \
    ScheduleJobVendorMappingSerializer
from .swagger_constants import POST_JOB_DISTRIBUTION, PUT_OPT_IN_OPT_OUT


class VendorJobMappingViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """
    Auto Job Distribution CRUD
    """
    authentication_classes = [RemoteJWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = VendorJobMapping.objects.all()
    serializer_class = VendorJobMappingSerializer
    filter_fields = ('program_id',
                     'job__id',
                     'job__uid',
                     'distribute_type',
                     'distribution_id',
                     'distribute_method',
                     'vendor_id',
                     'vendor_group_id',
                     'vendor_selection',
                     'opt_option'
                     )

    def get_serializer_context(self):
        context = super(VendorJobMappingViewSet, self).get_serializer_context()
        context.update({'token': self.request.META.get("HTTP_AUTHORIZATION"),
                        'ua': self.request.META.get("HTTP_USER_AGENT"),
                        "user_id": self.request.user.id,
                        "request": self.request
                        })
        return context

    @swagger_auto_schema(
        operation_description=POST_JOB_DISTRIBUTION,
        request_body=VendorJobMappingSerializerv2,
        responses={
            '201': "Created",
            '400': "Bad Request"
        }
    )
    def post(self, request, *args, **kwargs):
        '''
        Add VendorJobMapping data to the table
        '''
        # extracting the required data from the request objects
        vendor_id_data = request.data.get('vendors', [])
        vendor_group_id_data = request.data.get('vendor_group_id', [])
        distribution_id_data_obj = request.data.get('distribution_id', [])
        distribute_method = request.data.get('distribute_method', [])
        vendor_selection = request.data.get('vendor_selection', [])

        #  updating the program id in the request obj from the url kwargs
        request.data["program_id"] = str(kwargs["program_id"])

        # creating the empty vendor related lists
        vendor_id_obj_list = []

        try:
            settings.LOGGER.info(
                "VendorJobMappingView >> post >> request: {}".format(
                    request.data))

            # validate the request body and throw error if not valid
            obj = VendorJobMappingSerializerv2(data=request.data)

            if not obj.is_valid():
                settings.LOGGER.error(
                    "VendorJobMappingView >> post >> error: {}".format(
                        obj.errors))
                return Response({"error": "{}".format(obj.errors)},
                                status=status.HTTP_400_BAD_REQUEST)

            # checking required field/keys for the given distributed type
            distribute_type_obj = map_distribute_type(
                request.data['distribute_type'])

            for distribute_type in distribute_type_obj:
                if not request.data.get(distribute_type):
                    res_str = "{} fields are required in case of {}".format(
                        distribute_type_obj,
                        request.data['distribute_type'])
                    settings.LOGGER.info(
                        "VendorJobMappingView >> post >> response: {}".format(
                            res_str))
                    return Response(res_str)

            # scheduling the job to vendors when distribute_type is scheduled
            if request.data['distribute_type'] == "scheduled":
                vendor_id_obj_list = self.scheduled_job_distribution(
                    request,
                    distribution_id_data_obj=distribution_id_data_obj)

            # scheduling the job to vendors when distribute_type is manual
            elif request.data['distribute_type'] == "manual":
                vendor_id_obj_list = self.manual_job_distribution(
                    request,
                    vendor_id_data,
                    vendor_group_id_data)

            # scheduling the job to vendors when distribute_type is auto
            else:
                vendor_id_obj_list = self.auto_job_distribution(
                    request,
                    distribute_method, vendor_selection,
                    vendor_id_data, vendor_group_id_data)

            # passing job distribution data to vendor mapping serializers
            serializer = VendorJobMappingSerializer(
                data=vendor_id_obj_list,
                many=True,
                context={'token': request.META["HTTP_AUTHORIZATION"],
                         'ua': request.META["HTTP_USER_AGENT"],
                         "user_id": request.user.id,
                         "request": request
                         }
            )
            # validation the serialized data and save if validated
            if serializer.is_valid():
                serializer.save()

            # making the required response
            res_dict = {
                "data": serializer.data,
                "status": status.HTTP_200_OK
            }
            settings.LOGGER.info(
                "VendorJobMappingView >> post >> response: {}".format(
                    res_dict))
            # returning the response
            return Response(res_dict)
        except Exception as error:
            settings.LOGGER.error(
                "VendorJobMappingView >> post >> error: {}".format(
                    error))
            return Response({"error": "{}".format(error)},
                            status=status.HTTP_400_BAD_REQUEST)

    def scheduled_job_distribution(self, request,
                                   distribution_id_data_obj=None):
        """
        scheduling the job to vendors when distribute_type is scheduled

        :param request:
        :type request:
        :param distribution_id_data_obj:
        :type distribution_id_data_obj:
        :return:
        :rtype:
        """

        vendor_id_obj_list_final = []

        for distribution_id_data in distribution_id_data_obj:
            for scheduled_data in distribution_id_data['schedules']:

                if scheduled_data['schedule_unit'] == "IMMEDIATE":
                    # create vendor job mapping context for serializers
                    vendor_id_obj_list = self.parse_job_distribution_contexts(
                        request,
                        scheduled_data,
                        distribution_id_data)
                    vendor_id_obj_list_final.extend(vendor_id_obj_list)
                else:

                    schedule_unit = scheduled_data['schedule_unit'].lower()
                    scheduled_at = scheduled_data['schedule_value']

                    # try:
                    #     dt_next = datetime.datetime.strptime(
                    #         scheduled_at,
                    #         '%Y-%m-%dT%H:%M:%S.%fZ')

                    # except Exception as error:
                    #     raise Exception(
                    #         "error on the field after: {}".format(
                    #             error))

                    if "hour" in schedule_unit:
                        scheduled_at = int(scheduled_at) * 60 * 60

                    if "day" in schedule_unit:
                        scheduled_at = int(scheduled_at) * 60 * 60 * 24

                    if "week" in schedule_unit:
                        scheduled_at = int(scheduled_at) * 60 * 60 * 24 * 7

                    dt_now = datetime.datetime.now()
                    dt_next = dt_now + \
                              datetime.timedelta(seconds=int(scheduled_at))

                    vendor_id_obj_list = self.parse_job_distribution_contexts(
                        request,
                        scheduled_data,
                        distribution_id_data,
                        dt_next=dt_next
                    )

                    self.schedule_job_distribution(request,
                                                   vendor_id_obj_list,
                                                   True)

                    settings.SCHED.add_job(
                        self.schedule_job_distribution,
                        'date',
                        run_date=dt_next,
                        args=[request, vendor_id_obj_list, False]
                    )

        return vendor_id_obj_list_final

    def manual_job_distribution(self, request,
                                vendor_id_data=None,
                                vendor_group_id_data=None):
        """
        scheduling the job to vendors when distribute_type is manual

        :param request:
        :type request:
        :param vendor_id_data:
        :type vendor_id_data:
        :param vendor_group_id_data:
        :type vendor_group_id_data:
        :return:
        :rtype:
        """

        submission_limit = request.data.get("submission_limit")

        vendor_data = map_vendor_dict(
            request,
            request.data['program_id'],
            request.data['job_id'],
            request.data['distribute_type'],
            vendor_id_data,
            submission_limit=submission_limit
        )

        vendor_group_data = map_vendor_dict(
            request,
            request.data['program_id'],
            request.data['job_id'],
            request.data['distribute_type'],
            vendor_group_id_data,
            submission_limit=submission_limit,
            is_vendor_group_data=True
        )

        vendor_id_obj_list = vendor_data + vendor_group_data

        return vendor_id_obj_list

    def auto_job_distribution(self, request,
                              distribute_method, vendor_selection,
                              vendor_id_data, vendor_group_id_data):
        """
        scheduling the job to vendors when distribute_type is auto

        :param request:
        :type request:
        :param distribute_method:
        :type distribute_method:
        :param vendor_selection:
        :type vendor_selection:
        :param vendor_id_data:
        :type vendor_id_data:
        :param vendor_group_id_data:
        :type vendor_group_id_data:
        :return:
        :rtype:
        """
        submission_limit = request.data.get("submission_limit")

        if vendor_selection == 'manual_input':
            vendor_id_list = vendor_id_data
        else:
            # based on industry and region
            vendor_list = []
            vendor_group_id_data = []

            job_obj = Job.objects.get(uid=request.data['job_id'])
            industry_obj = job_obj.category.job_catalog.all().values(
                'naics_code__industry_type'
            )
            industry_list = [industry['naics_code__industry_type']
                             for industry in industry_obj]

            # region_data = job_obj.foundational.work_location

            vendor_program_data = get_vendors(
                request,
                settings.VENDOR_ENDPOINT,
                request.data['program_id']
            )

            for vendor_industry_data in vendor_program_data:
                vendor_name = vendor_industry_data['vendor']['id']
                vendor_group_id_list = vendor_industry_data['vendor_groups']
                get_vendor_group_list = []

                for vendor_group_id in vendor_group_id_list:
                    get_vendor_group_list.append(vendor_group_id['id'])

                for vendor_group_id in get_vendor_group_list:
                    try:
                        group_vendor_list = get_vendors_based_on_group_id(
                            request,
                            settings.VENDOR_ENDPOINT,
                            request.data['program_id'],
                            vendor_group_id,
                        )
                    except Exception as error:
                        settings.LOGGER.error(
                            "VendorJobMappingView >> post >> Problem fetching Vendor: error: {} {}".format(
                                error,
                                vendor_group_id
                            ))
                        continue

                    for vendor_obj in group_vendor_list:
                        vendor_industry_name = vendor_obj['industries']
                        vendor_group_list = []
                        for vendor_industry in vendor_obj['industries']:
                            for industry in industry_list:
                                if industry in vendor_industry['name']:
                                    vendor_group_list.append(
                                        vendor_obj['id'])
                                    context = {
                                        "id": vendor_group_id,
                                        "vendor_id": vendor_group_list
                                    }

                                    vendor_group_id_data.append(context)

                for vendor_industry in vendor_industry_data['vendor'][
                    'industries']:
                    for industry in industry_list:
                        if industry in vendor_industry['name']:
                            vendor_list.append(vendor_name)

            vendor_id_list = vendor_list
            vendor_group_id_list = vendor_group_id_data

        vendor_data = map_vendor_dict(
            request,
            request.data['program_id'],
            request.data['job_id'],
            request.data['distribute_type'],
            vendor_id_list,
            distribute_method,
            vendor_selection,
            submission_limit=submission_limit

        )

        vendor_group_data = map_vendor_dict(
            request,
            request.data['program_id'],
            request.data['job_id'],
            request.data['distribute_type'],
            vendor_group_id_data,
            distribute_method,
            vendor_selection,
            submission_limit=submission_limit,
            is_vendor_group_data=True
        )
        vendor_id_obj_list = vendor_data + vendor_group_data

        return vendor_id_obj_list

    @staticmethod
    def schedule_job_distribution(request, vendor_id_obj_list,
                                  keep_data_separate=True):
        """
        schedule the job to vendors at particular date
        :param request:
        :type request:
        :param vendor_id_obj_list:
        :type vendor_id_obj_list:
        :param keep_data_separate:
        :type keep_data_separate:
        :return:
        :rtype:
        """
        try:
            settings.LOGGER.info(
                "VendorJobMappingView >> schedule_job_distribution >> request: {}".format(
                    request.GET))

            if vendor_id_obj_list:
                if keep_data_separate:
                    serializer = ScheduleJobVendorMappingSerializer(
                        data=vendor_id_obj_list,
                        many=True,
                        context={'token': request.META["HTTP_AUTHORIZATION"],
                                 'ua': request.META["HTTP_USER_AGENT"],
                                 "user_id": request.user.id,
                                 "request": request
                                 }
                    )
                else:
                    serializer = VendorJobMappingSerializer(
                        data=vendor_id_obj_list,
                        many=True,
                        context={'token': request.META["HTTP_AUTHORIZATION"],
                                 'ua': request.META["HTTP_USER_AGENT"],
                                 "user_id": request.user.id,
                                 "request": request
                                 }
                    )
                if serializer.is_valid():
                    serializer.save()
        except Exception as error:
            settings.LOGGER.error(
                "VendorJobMappingView >> schedule_job_distribution >> error: {}".format(
                    error))
            raise Exception(error)

    def parse_job_distribution_contexts(self, request, scheduled_data,
                                        distribution_id_data, dt_next=None):
        """
        create context for the VendorJobMappingSerializer

        :param request:
        :type request:
        :param scheduled_data:
        :type scheduled_data:c
        :param distribution_id_data:
        :type distribution_id_data:
        :param dt_next:
        :type dt_next:
        :return:
        :rtype:
        """

        vendor_id_obj_list = []

        submission_limit = request.data.get("submission_limit")

        for vendor_id in scheduled_data.get('vendors', []):
            context = {
                'program_id': request.data['program_id'],
                'job_id': request.data['job_id'],
                'distribute_type': request.data['distribute_type'],
                'vendor_id': vendor_id,
                'distribution_id': distribution_id_data['id'],
                'schedule_type': scheduled_data['schedule_unit'],

            }
            if submission_limit:
                context.update({
                    "submission_limit": submission_limit
                })
            if dt_next:
                context.update({
                    'scheduled_datetime': str(dt_next)
                })

            vendor_id_obj_list.append(context)

        for vendor_group_id in scheduled_data.get('vendor_group_id', []):

            try:
                vendor_list = get_vendors_based_on_group_id(
                    request,
                    settings.VENDOR_ENDPOINT,
                    request.data['program_id'],
                    vendor_group_id
                )
            except Exception as error:
                settings.LOGGER.error(
                    "VendorJobMappingView >> post >> Problem fetching Vendor: error: {} {}".format(
                        error,
                        vendor_group_id
                    ))
                continue

            for vendor_obj in vendor_list:
                context = {
                    'program_id': request.data['program_id'],
                    'job_id': request.data['job_id'],
                    'distribute_type': request.data['distribute_type'],
                    'vendor_id': vendor_obj["id"],
                    'vendor_group_id': vendor_group_id,
                    'distribution_id': distribution_id_data['id'],
                    'schedule_type': scheduled_data['schedule_unit'],
                }

                if submission_limit:
                    context.update({
                        "submission_limit": submission_limit
                    })
                if dt_next:
                    context.update({
                        'scheduled_datetime': str(dt_next)
                    })

                vendor_id_obj_list.append(context)

        return vendor_id_obj_list

    def filter_queryset(self, queryset):
        """
        Given a queryset, filter it with whichever filter backend is in use.

        You are unlikely to want to override this method, although you may need
        to call it either from a list view, or from a custom `get_object`
        method if you want to apply the configured filtering backend to the
        default queryset.
        """

        # for backend in list(self.filter_backends):
        #     queryset = backend().filter_queryset(self.request, queryset, self)
        queryset = queryset.select_related().filter(
            program_id=self.kwargs["program_id"])

        filter_fields = {key: val for key, val in
                         self.request.query_params.items() if
                         key in self.filter_fields}

        if filter_fields:
            queryset = queryset.filter(**filter_fields)

        if not filter_fields.get("opt_option"):
            queryset = queryset.exclude(opt_option="opt_out")

        return queryset

    def get_list(self, request, *args, **kwargs):
        """
        """
        try:
            settings.LOGGER.info(
                "VendorJobConfigurationViewSet >> get_list >> request: {}".format(
                    request.GET))
            program_id = str(kwargs["program_id"])

            self.queryset = self.queryset.filter(
                Q(program_id="0") | Q(program_id=program_id))

            response = self.list(request, *args, **kwargs)

            scheduled_job_list = ScheduleJobVendorMapping.objects.select_related().filter(
                program_id=program_id, scheduled_status="scheduling")

            if self.request.query_params.get("job__uid"):
                scheduled_job_list = scheduled_job_list.filter(
                    job__uid=self.request.query_params.get("job__uid"))

            if self.request.query_params.get("job__id"):
                scheduled_job_list = scheduled_job_list.filter(
                    job__id=self.request.query_params.get("job__id"))

            if self.request.query_params.get("distribute_type"):
                scheduled_job_list = scheduled_job_list.filter(
                    distribute_type=self.request.query_params.get(
                        "distribute_type"))

            if self.request.query_params.get("distribution_id"):
                scheduled_job_list = scheduled_job_list.filter(
                    distribution_id=self.request.query_params.get(
                        "distribution_id"))

            if self.request.query_params.get("vendor_id"):
                scheduled_job_list = scheduled_job_list.filter(
                    vendor_id=self.request.query_params.get("vendor_id"))

            if self.request.query_params.get("vendor_group_id"):
                scheduled_job_list = scheduled_job_list.filter(
                    vendor_group_id=self.request.query_params.get(
                        "vendor_group_id"))

            if self.request.query_params.get("vendor_selection"):
                scheduled_job_list = scheduled_job_list.filter(
                    vendor_selection=self.request.query_params.get(
                        "vendor_selection"))

            # if self.request.query_params.get("opt_option"):
            #     scheduled_job_list = scheduled_job_list.filter(
            #         opt_option=self.request.query_params.get("opt_option"))

            serialized_scheduled_job = ScheduleJobVendorMappingSerializer(
                scheduled_job_list, many=True,
                context={'token': request.META["HTTP_AUTHORIZATION"],
                         'ua': request.META["HTTP_USER_AGENT"],
                         "user_id": request.user.id,
                         "request": request
                         }
            )

            response.data.update({"program_id": program_id,
                                  "scheduled_job": serialized_scheduled_job.data})
            settings.LOGGER.info(
                "VendorJobConfigurationViewSet >> get_list >> response: {}".format(
                    response.status_code))
            return response
        except Exception as error:
            settings.LOGGER.error(
                "VendorJobConfigurationViewSet >> get_list >> error: {}".format(
                    error))
            return Response({"error": "{}".format(error)},
                            status=status.HTTP_400_BAD_REQUEST)

    def get_object(self):
        """
        Returns the object the view is displaying.

        You may want to override this if you need to provide non-standard
        queryset lookups.  Eg if objects are referenced using multiple
        keyword arguments in the url conf.
        """

        queryset = self.filter_queryset(self.get_queryset())

        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        assert lookup_url_kwarg in self.kwargs, (
                'Expected view %s to be called with a URL keyword argument '
                'named "%s". Fix your URL conf, or set the `.lookup_field` '
                'attribute on the view correctly.' %
                (self.__class__.__name__, lookup_url_kwarg)
        )

        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        filter_kwargs.update({"program_id": self.kwargs["program_id"]})
        obj = get_object_or_404(queryset, **filter_kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj

    def get(self, request, *args, **kwargs):
        """
        """
        try:
            settings.LOGGER.info(
                "VendorJobConfigurationViewSet >> get >> request: {}".format(
                    request.GET))

            try:
                response = self.retrieve(request, *args, **kwargs)
                response = response.data
            except Exception as error:
                queryset = ScheduleJobVendorMapping.objects.select_related().filter(
                    **kwargs)
                serialized_scheduled_job = ScheduleJobVendorMappingSerializer(
                    queryset, many=True,
                    context={'token': request.META["HTTP_AUTHORIZATION"],
                             'ua': request.META["HTTP_USER_AGENT"],
                             "user_id": request.user.id,
                             "request": request
                             }
                )
                res = serialized_scheduled_job.data
                response = res[0] if res else {}

            response.update({"program_id": kwargs["program_id"]})

            settings.LOGGER.info(
                "VendorJobConfigurationViewSet >> get >> response: {}".format(
                    response))
            return Response(response,
                            status=status.HTTP_200_OK)

        except Exception as error:
            settings.LOGGER.error(
                "VendorJobConfigurationViewSet >> get >> error: {}".format(
                    error))
            return Response({"error": "{}".format(error)},
                            status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        """
        """
        request.data["program_id"] = str(kwargs["program_id"])

        try:
            settings.LOGGER.info(
                "VendorJobConfigurationViewSet >> put >> request: {}".format(
                    request.data))
            response = self.update(request, *args, **kwargs)
            settings.LOGGER.info(
                "VendorJobConfigurationViewSet >> put >> response: {}".format(
                    response.data))
            return response
        except Exception as error:
            settings.LOGGER.error(
                "VendorJobConfigurationViewSet >> put >> error: {}".format(
                    error))
            return Response({"error": "{}".format(error)},
                            status=status.HTTP_400_BAD_REQUEST)

    def update_schedule_data(self, request, *args, **kwargs):
        """
        update scheduled data
        :param request:
        :type request:
        :param args:
        :type args:
        :param kwargs:
        :type kwargs:
        :return:
        :rtype:
        """

        partial = kwargs.pop('partial', False)
        queryset = ScheduleJobVendorMapping.objects.select_related().filter(
            **kwargs)
        instance = get_object_or_404(queryset, **kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, instance)

        serializer = ScheduleJobVendorMappingSerializer(
            instance,
            data=request.data,
            partial=partial,
            context={'token': request.META["HTTP_AUTHORIZATION"],
                     'ua': request.META["HTTP_USER_AGENT"],
                     "user_id": request.user.id,
                     "request": request
                     }
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        """
        """
        try:
            settings.LOGGER.info(
                "VendorJobConfigurationViewSet >> delete >> request: {}".format(
                    request.path))
            response = self.destroy(request, *args, **kwargs)
            settings.LOGGER.info(
                "VendorJobConfigurationViewSet >> delete >> response: {}".format(
                    response.status_code))
            return response
        except Exception as error:
            settings.LOGGER.error(
                "VendorJobConfigurationViewSet >> delete >> error: {}".format(
                    error))
            return Response({"error": "{}".format(error)},
                            status=status.HTTP_400_BAD_REQUEST)

    def destroy_scheduled_data(self, request, *args, **kwargs):
        """
        perform destroy scheduled data

        :param request:
        :type request:
        :param args:
        :type args:
        :param kwargs:
        :type kwargs:
        :return:
        :rtype:
        """

        queryset = ScheduleJobVendorMapping.objects.select_related().filter(
            **kwargs)
        instance = get_object_or_404(queryset, **kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, instance)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        operation_description=PUT_OPT_IN_OPT_OUT,
        request_body=OptInOptOutSerializer,
        responses={
            '204': "resource updated successfully",
            '400': "Bad Request"
        }
    )
    def opt_in_opt_out(self, request, *args, **kwargs):
        """
        opt out or opt in for the given program_id, verndor_id and job_id
        """
        try:
            settings.LOGGER.info(
                "VendorJobConfigurationViewSet >> opt_in_opt_out >> request: {}".format(
                    kwargs))
            program_id = kwargs["program_id"]
            vendor_id = kwargs["vendor_id"]
            job_id = kwargs["job_id"]
            opt_option_dict = {}
            opt_option = request.data["opt_option"]
            reason = request.data.get("reason")

            if job_id.isnumeric():
                vendor_obj = VendorJobMapping.objects.filter(
                    program_id=program_id, job_id=int(job_id),
                    vendor_id=vendor_id)
            else:
                vendor_obj = VendorJobMapping.objects.filter(
                    program_id=program_id, job__uid=job_id, vendor_id=vendor_id)

            opt_option_dict = {"opt_option": opt_option}
            if reason:
                opt_option_dict.update({"reason": reason})

            # validate the request body and throw error if not valid
            obj = OptInOptOutSerializer(data=request.data)

            if not obj.is_valid():
                settings.LOGGER.error(
                    "opt_in_opt_out >> post >> error: {}".format(
                        obj.errors))
                return Response({"error": "{}".format(obj.errors)},
                                status=status.HTTP_400_BAD_REQUEST)

            vendor_obj.update(**opt_option_dict)
            serializer = VendorJobMappingSerializer(
                vendor_obj, many=True,
                context={'token': request.META["HTTP_AUTHORIZATION"],
                         'ua': request.META["HTTP_USER_AGENT"],
                         "user_id": request.user.id,
                         "request": request
                         })
            response = Response(serializer.data)
            settings.LOGGER.info(
                "VendorJobConfigurationViewSet >> opt_in_opt_out >> response: {}".format(
                    response.status_code))
            return response
        except Exception as error:
            settings.LOGGER.error(
                "VendorJobConfigurationViewSet >> opt_in_opt_out >> error: {}".format(
                    error))
            return Response({"error": "{}".format(error)},
                            status=status.HTTP_400_BAD_REQUEST)


class ScheduleJobVendorMappingViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    Auto Job Distribution CRUD
    """
    authentication_classes = [RemoteJWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = ScheduleJobVendorMapping.objects.all()
    serializer_class = ScheduleJobVendorMappingSerializer
    filter_fields = ('program_id',
                     'job__id',
                     'job__uid',
                     'distribute_type',
                     'vendor_id',
                     'vendor_group_id',
                     'distribution_id',
                     'scheduled_datetime',
                     'scheduled_status'
                     )

    def get_serializer_context(self):
        context = super(ScheduleJobVendorMappingViewSet,
                        self).get_serializer_context()
        context.update({'token': self.request.META.get("HTTP_AUTHORIZATION"),
                        'ua': self.request.META.get("HTTP_USER_AGENT"),
                        "user_id": self.request.user.id,
                        "request": self.request
                        })
        return context

    def get_object(self):
        """
        Returns the object the view is displaying.

        You may want to override this if you need to provide non-standard
        queryset lookups.  Eg if objects are referenced using multiple
        keyword arguments in the url conf.
        """

        queryset = self.filter_queryset(self.get_queryset())

        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        assert lookup_url_kwarg in self.kwargs, (
                'Expected view %s to be called with a URL keyword argument '
                'named "%s". Fix your URL conf, or set the `.lookup_field` '
                'attribute on the view correctly.' %
                (self.__class__.__name__, lookup_url_kwarg)
        )

        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        filter_kwargs.update({"program_id": self.kwargs["program_id"]})
        obj = get_object_or_404(queryset, **filter_kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj

    def get(self, request, *args, **kwargs):
        """
        """
        try:
            settings.LOGGER.info(
                "ScheduleJobVendorMappingViewSet >> get >> request: {}".format(
                    request.GET))
            response = self.retrieve(request, *args, **kwargs)
            settings.LOGGER.info(
                "ScheduleJobVendorMappingViewSet >> get >> response: {}".format(
                    response.data))
            return response
        except Exception as error:
            settings.LOGGER.error(
                "ScheduleJobVendorMappingViewSet >> get >> error: {}".format(
                    error))
            return Response({"error": "{}".format(error)},
                            status=status.HTTP_400_BAD_REQUEST)

    def get_list(self, request, *args, **kwargs):
        """
        """
        try:
            settings.LOGGER.info(
                "ScheduleJobVendorMappingViewSet >> get_list >> request: {}".format(
                    request.GET))
            program_id = str(kwargs["program_id"])

            self.queryset = self.queryset.filter(
                Q(program_id="0") | Q(program_id=program_id))

            response = self.list(request, *args, **kwargs)
            response.data.update({"program_id": program_id})
            settings.LOGGER.info(
                "ScheduleJobVendorMappingViewSet >> get_list >> response: {}".format(
                    response.status_code))
            return response
        except Exception as error:
            settings.LOGGER.error(
                "ScheduleJobVendorMappingViewSet >> get_list >> error: {}".format(
                    error))
            return Response({"error": "{}".format(error)},
                            status=status.HTTP_400_BAD_REQUEST)
