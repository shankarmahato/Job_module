from distutils.util import strtobool

from django.conf import settings
from django.db.models import Q, F
from django.http import Http404
from django.utils.datastructures import MultiValueDictKeyError
from drf_yasg.utils import swagger_auto_schema
from pyexcel_xls import get_data as xls_get
from pyexcel_xlsx import get_data as xlsx_get
from rest_framework import filters
from rest_framework import mixins
from rest_framework import status
from rest_framework import viewsets
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from job_catalog.models import JobCatalog, JobTitle, JobTag
from job_catalog.models import JobCategory, Industry
from job_catalog.serializers import (JobTitleSerializer,
                                     JobTitleReadSerializer,
                                     JobCatalogSerializer,
                                     IndustrySerializer,
                                     CategorySerializer,
                                     JobCategoryTitleSerializer)
from .job_catalog_constants import SORT_BY_REFERENCE_DICT, EDITABLE_FIELDS, \
    ErrorMessage
from .swagger_constants import UPLOAD_INDUSTRIES, UPLOAD_CATEGORY, \
    GET_JOB_TITLES, POST_JOB_TITLE, JobTitleQueryParams, GET_JOB_TITLE, \
    PUT_JOB_TITLE, DELETE_JOB_TITLE, UPLOAD_JOB_TITLE, GET_JOB_CATALOG, \
    JobCatalogQueryParams, GET_SINGLE_JOB_CATALOG, PUT_SINGLE_JOB_CATALOG, POST_JOB_CATALOG
from job.utils import PaginationHandlerMixin

from connectors.vms_profile_manager.auth import IsAuthenticated, RemoteJWTAuthentication
from django.core.paginator import Paginator
from job.pagination import JobsPagination
from rest_framework import mixins
from rest_framework import generics
from  collections import OrderedDict



class IndustryViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                      viewsets.GenericViewSet):
    """
    This view contains the list of all industries with naics code
    and industry type that is defined by the system and is not
    going to change very frquently.
    """
    authentication_classes = [RemoteJWTAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = Industry.objects.all()
    serializer_class = IndustrySerializer
    filter_fields = ('naics_code', 'industry_type')
    search_fields = ('naics_code', 'industry_type')

    def get(self, request, *args, **kwargs):
        instance = Industry.objects.get(uid=kwargs["uid"])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class IndustryImportView(APIView):
    """
    Import Industries from xlsx/xls files
    """


    @swagger_auto_schema(
        operation_description=UPLOAD_INDUSTRIES,
        responses={
            '201': "Created",
            '400': "Bad Request"
        }
    )
    def post(self, request, format=None):
        """
        Import Industries from xlsx/xls files
        :param request:
        :type request:
        :param format:
        :type format:
        :return:
        :rtype:
        """

        try:
            excel_file = request.data["files"]
        except MultiValueDictKeyError:
            raise Exception("Excel files needs to be uploaded!!")

        file_type = str(excel_file).split('.')[-1]

        if file_type == "xls":
            data = xls_get(excel_file, start_row=1)
        elif file_type == "xlsx":
            data = xlsx_get(excel_file, start_row=1)
        else:
            return Response('Only xls and xlsx file types are allowed')

        try:
            for obj in data['Sheet1']:
                try:
                    Industry.objects.get_or_create(
                        naics_code=obj[1], industry_type=obj[2])
                except Exception as error:
                    settings.LOGGER.info(
                        "IndustryImportView >> post >> error: {}, data: {}".format(
                            error, obj))

            return Response({
                "result": "Industry Successfully exported!!",
                "status": status.HTTP_201_CREATED
            })
        except Exception as error:
            settings.LOGGER.info(
                "IndustryImportView >> post >> error: {}".format(error))
            return Response({"error": "{}".format(error)},
                            status=status.HTTP_400_BAD_REQUEST)


class CategoryView(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                   viewsets.GenericViewSet):
    """
    This view contains the list of all categories with o_net_soc_code,
    category name and description that is defined by the system and is not
    going to change very frequently.
    Description from this table will be used by the job title at first upon
    selecting the job category while creating job title.
    """
    authentication_classes = [RemoteJWTAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = JobCategory.objects.all()
    serializer_class = CategorySerializer
    filterset_fields = ['category_name', 'o_net_soc_code']
    filter_backends = [filters.SearchFilter]
    search_fields = ['category_name', 'o_net_soc_code']

    def get(self, request, *args, **kwargs):
        instance = JobCategory.objects.get(uid=kwargs["uid"])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class CategoryImportView(APIView):
    """
    Import Category from xlsx/xls files
    """

    @swagger_auto_schema(
        operation_description=UPLOAD_CATEGORY,
        responses={
            "201": "Created",
            "400": "Bad Request"
        }
    )
    def post(self, request, format=None):
        """
        import category from xlsx/xls files
        :param request:
        :type request:
        :param format:
        :type format:
        :return:
        :rtype:
        """
        try:
            excel_file = request.data["files"]
        except MultiValueDictKeyError:
            raise Exception("Excel files needs to be uploaded!!")

        file_type = str(excel_file).split('.')[-1]

        if file_type == "xls":
            data = xls_get(excel_file, start_row=1)
        elif file_type == "xlsx":
            data = xlsx_get(excel_file, start_row=1)
        else:
            return Response('Only xls and xlsx file types are allowed')

        try:
            for obj in data["Job Category List"]:
                try:
                    JobCategory.objects.get_or_create(
                        o_net_soc_code=obj[0], category_name=obj[1],
                        description=obj[2])
                except Exception as error:
                    settings.LOGGER.info(
                        "CategoryImportView >> post >> error: {}, data: {}".format(
                            error, obj))
            return Response({
                "count": len(data["Job Category List"]),
                "result": "Category Successfully Imported!!",
                "status": status.HTTP_201_CREATED
            })
        except Exception as error:
            settings.LOGGER.info(
                "CategoryImportView >> post >> error: {}".format(error))
            return Response({"error": "{}".format(error)},
                            status=status.HTTP_400_BAD_REQUEST)


class JobTitleView(APIView):
    """
    This view helps to get all the existing job titles
    and helps to create a new one. The job title, category
    and program id are unique to each other
    """
    authentication_classes = [RemoteJWTAuthentication]
    permission_classes = [IsAuthenticated]

    pagination_class = LimitOffsetPagination

    def get_object(self):
        """
        Get all the current JobTitle objects
        existing in the system.
        :return:
        :rtype:
        """
        try:
            q_object = self.make_complex_query_set()
            if q_object:
                obj = JobTitle.objects.filter(q_object).distinct()
            else:
                obj = JobTitle.objects.all()

            # Retrieving Data
            paginator = LimitOffsetPagination()
            results = paginator.paginate_queryset(obj, self.request)
            return results
        except JobTitle.DoesNotExist:
            raise Http404

    @swagger_auto_schema(
        operation_description=GET_JOB_TITLES,
        query_serializer=JobTitleQueryParams,
        responses={
            "200": "Success",
            "400": "Bad Request"
        }

    )
    def get(self, request, format=None):
        """
        Method to list down all the job titles of a program id
        available in the system whose status is active.

        :param request:
        :type request:
        :param format:
        :type format:
        :return:
        :rtype:
        """
        settings.LOGGER.info(
            "JobTitleView >> get >> request: {}".format(request.GET))
        try:
            serializer = JobTitleReadSerializer(self.get_object(), many=True)
            res = {
                "data": serializer.data,
                "status": status.HTTP_200_OK
            }

            settings.LOGGER.info(
                "JobTitleView >> get >> response: {}".format(res))
            return Response(res)
        except Exception as e:
            settings.LOGGER.info(
                "JobTitleView >> get >> error: {}".format(e))
            return Response({"error": "{}".format(e)},
                            status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description=POST_JOB_TITLE,
        request_body=JobTitleSerializer,
    )
    def post(self, request):
        """
        Add a job title  with system defined category and
        program id, the program id , category and job title
        makes a unique set.
        Note:
        A job title may have multiple job tags while creating a
        new job title.

        A job title table will have description of the category selected
        at first latter user can modify it making no changes to category table
        description field.

        :param request:
        :type request:
        :return:
        :rtype:
        """

        settings.LOGGER.info(
            "JobTitleView >> post >> request: {}".format(request.POST))

        try:
            serializer = JobTitleSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                settings.LOGGER.info(
                    "JobTitleView >> post >> response: {}".format(
                        serializer.data))
                serializer = JobTitleReadSerializer(
                    instance=serializer.instance)
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )
            else:
                error = serializer.errors

        except Exception as e:
            error = e
        settings.LOGGER.info(
            "JobTitleView >> post >> error: {}".format(error))
        return Response({"error": "{}".format(error)},
                        status=status.HTTP_400_BAD_REQUEST)

    def make_complex_query_set(self):
        """
        function to search, filter and sort the job catalog with
        making complex queryset for filtering the job catalog

        :return:
        :rtype:
        """

        query = self.request.GET.get("q")
        program_id = self.request.META.get('HTTP_X_SVMS_PROGRAM_ID')
        category = self.request.GET.get("category")
        title = self.request.GET.get("title")
        level = self.request.GET.get("level")
        description = self.request.GET.get("description")
        status = self.request.GET.get("status")
        job_tag = self.request.GET.get("job_tag")

        q_object = Q()

        if query:
            q_object.add((
                Q(program_id=query) |
                Q(category=query) |
                Q(title__icontains=query) |
                #Q(category__category_name__icontains=query) |
                Q(description__icontains=query) |
                Q(job_tag__tag__in=str(query).split(","))
            ), Q.OR)

            if query.isnumeric():
                q_object.add(
                    Q(level__icontains=int(query)), Q.OR)

            q_object.add(Q(status=strtobool(query)), Q.OR) if query in [
                "true", "True", "False", "false"] else None

        else:
            if program_id:
                q_object.add(
                    Q(program_id=program_id),
                    Q.AND)

            if category:
                q_object.add(
                    Q(category=category),
                    Q.AND)
            if title:
                q_object.add(
                    Q(title__icontains=title),
                    Q.AND)

            if description:
                q_object.add(
                    Q(description__icontains=description), Q.AND)

            if job_tag:
                q_object.add(
                    Q(job_tag__tag__in=str(job_tag).split(",")),
                    Q.AND)

            if level:
                if level.isnumeric():
                    q_object.add(
                        Q(level__icontains=int(level)),
                        Q.AND)
                else:
                    raise Exception(
                        ErrorMessage.WRONG_FIELD_TYPE.value.format("level",
                                                                   "numeric"))

            q_object.add(Q(status=strtobool(status)), Q.AND) if status in [
                "true", "True", "False", "false"] else None

        return q_object


class JobTitleDetailView(APIView):
    """
    Retrieve, update or delete a snippet instance.

    """
    authentication_classes = [RemoteJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        """
        Method list down the detail of a specific job title
        record with the help of the primary key provide in the
        url of the request.

        :param pk:
        :type pk:
        :return:
        :rtype:
        """
        try:
            return JobTitle.objects.get(Q(id=pk) | Q(uid=pk))
        except JobTitle.DoesNotExist:
            raise Http404

    @swagger_auto_schema(
        operation_description=GET_JOB_TITLE,
        responses={
            "200": "Success",
            "400": "Bad Request"
        }
    )
    def get(self, request, pk, format=None):
        """
        Method list down the detail of a specific job title
        record with the help of the primary key provide in the
        url of the request.

        :param request:
        :type request:
        :param pk:
        :type pk:
        :param format:
        :type format:
        :return:
        :rtype:
        """

        settings.LOGGER.info(
            "JobTitleDetailView >> get >> request: {}".format(request.GET))
        try:
            obj = self.get_object(pk)
            serializer = JobTitleReadSerializer(obj)
            settings.LOGGER.info(
                "JobTitleDetailView >> get >> response: {}".format(
                    serializer.data))
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            settings.LOGGER.info(
                "JobTitleDetailView >> get >> error: {}".format(e))
            return Response({"error": "{}".format(e)},
                            status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description=PUT_JOB_TITLE,
        request_body=JobTitleSerializer,
        responses={
            '202': "Accepted",
            '400': "Bad Request"
        }
    )
    def put(self, request, pk, format=None):
        """
        Method helps to update a job title record with the help
        of a primary key provided in the requested url.
        Note:
        Program id, system defined category and job title field
        must be unique.

        :param request:
        :type request:
        :param pk:
        :type pk:
        :param format:
        :type format:
        :return:
        :rtype:
        """
        settings.LOGGER.info(
            "JobTitleDetailView >> put >> request: {}, pk: {}".format(
                request.query_params, pk))
        try:
            obj = self.get_object(pk)
            serializer = JobTitleSerializer(obj, data=request.data)
            if serializer.is_valid():
                serializer.save()
                serializer = JobTitleReadSerializer(
                    instance=serializer.instance)
                settings.LOGGER.info(
                    "JobTitleDetailView >> put >> response: {}".format(
                        serializer.data))
                return Response(serializer.data,
                                status=status.HTTP_202_ACCEPTED)
            else:
                error = serializer.errors
        except Exception as e:
            error = e
        settings.LOGGER.info(
            "JobTitleDetailView >> put >> error: {}".format(error))
        return Response({"error": "{}".format(error)},
                        status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description=DELETE_JOB_TITLE,
        responses={
            "204": "No Content",
            "400": "Bad Request"
        }
    )
    def delete(self, request, pk, format=None):
        """
        Method helps to delete a job title record of a program id
        with the help of the primary key provided in the requested url.

        :param request:
        :type request:
        :param pk:
        :type pk:
        :param format:
        :type format:
        :return:
        :rtype:
        """
        settings.LOGGER.info(
            "JobTitleDetailView >> delete >> request pk: {}".format(pk))

        try:
            obj = self.get_object(pk)
            obj.delete()
            settings.LOGGER.info(
                "JobTitleDetailView >> delete >> pk {}, success".format(pk))
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            settings.LOGGER.info(
                "JobTitleDetailView >> delete >> pk {}, error: {}".format(pk,
                                                                          e))
            return Response({"error": "{}".format(e)},
                            status=status.HTTP_400_BAD_REQUEST)


class JobTitleImportView(APIView):
    """
    Import Job Title from xlsx/xls files
    """

    @swagger_auto_schema(
        operation_description=UPLOAD_JOB_TITLE,
        responses={
            "201": "created",
            "400": "Bad Request"
        }
    )
    def post(self, request, format=None):
        """
        import Job Title from xlsx/xls files
        :param request:
        :type request:
        :param format:
        :type format:
        :return:
        :rtype:
        """
        try:
            excel_file = request.data["files"]
        except MultiValueDictKeyError:
            raise Exception("Excel file needs to be uploaded!!")

        file_type = str(excel_file).split('.')[-1]

        if file_type == "xls":
            data = xls_get(excel_file, start_row=1)
        elif file_type == "xlsx":
            data = xlsx_get(excel_file, start_row=1)
        else:
            return Response('Only xls and xlsx file types are allowed')

        try:
            for obj in data["Job Titles"]:
                try:
                    category_obj, _ = JobCategory.objects.get_or_create(
                        o_net_soc_code=obj[0], category_name=obj[1])

                    tag_list = []
                    if obj.__len__() == 4:
                        for o in obj[3].split(","):
                            tag_obj, _ = JobTag.objects.get_or_create(tag=o)
                            tag_list.append(tag_obj)

                    job_title_obj, _ = JobTitle.objects.get_or_create(
                        program_id=0,
                        category=category_obj,
                        title=obj[2],
                        level=1,
                        description=category_obj.description,
                        created_by=request.user,
                        modified_by=request.user
                    )
                    if tag_list:
                        job_title_obj.job_tag.clear()
                        job_title_obj.job_tag.add(*tag_list)
                        job_title_obj.save()

                except Exception as error:
                    settings.LOGGER.info(
                        "JobTitleImportView >> post >> error: {}, data: {}".format(
                            error, obj))
            return Response({
                "count": len(data["Job Titles"]),
                "result": "Job Title Successfully Imported!!",
                "status": status.HTTP_201_CREATED
            })
        except Exception as error:
            settings.LOGGER.info(
                "JobTitleImportView >> post >> error: {}".format(error))
            return Response({"error": "{}".format(error)},
                            status=status.HTTP_400_BAD_REQUEST)


class JobCatalogViewList(APIView):
    """
    JOb Catalog View for a specific record
    """
    authentication_classes = [RemoteJWTAuthentication]
    permission_classes = [IsAuthenticated]

    pagination_class = LimitOffsetPagination

    def get_object(self):
        """
        Get a all record of the JobCatalog
        available on the system having status
        to be active.

        :return:
        :rtype:
        """
        try:
            q_object = self.make_complex_query_set()
            order_by_list = self.make_order_by_combination()

            if q_object:
                obj = JobCatalog.objects.filter(q_object).distinct()
            else:
                obj = JobCatalog.objects.all()

            if order_by_list:
                obj = obj.order_by(*order_by_list)

            # Retrieving Data
            paginator = LimitOffsetPagination()
            results = paginator.paginate_queryset(obj, self.request)
            return results

        except JobCatalog.DoesNotExist:
            raise Http404

    @swagger_auto_schema(
        operation_description=GET_JOB_CATALOG,
        query_serializer=JobCatalogQueryParams,
        responses={
            '200': "Success",
            '400': "Bad Request"
        }
    )
    def get(self, request, format=None):
        """
        Method to list down details of all the system defined industry
        ,system defined category with job title forming unique set with
        job category, having status to be true.
        Note:
        Perform search, filter and sorting of the fields like job title
        job level,job description, o_net_soc_code and category name and 
        description.
        :param request:
        :type request:
        :param format:
        :type format:
        :return:
        :rtype:
        """

        settings.LOGGER.info(
            "JobCatalogViewList >> get >> request {}".format(request.GET))
        try:
            catalog_obj = self.get_object()
            program_id = request.META.get('HTTP_X_SVMS_PROGRAM_ID', None)
            context = {'program_id': program_id, "request_obj": self.request}
            serializer = JobCatalogSerializer(
                catalog_obj, many=True, context=context)
            res = {
                "data": serializer.data,
                "status": status.HTTP_200_OK
            }
            settings.LOGGER.info(
                "JobCatalogViewList >> get >> response {}".format(res))
            return Response(res)
        except Exception as e:
            settings.LOGGER.info(
                "JobCatalogViewList >> get >> error {}".format(e))
            return Response({"error": "{}".format(e)},
                            status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description=POST_JOB_CATALOG,
    )
    def post(self, request):
        """
        Post job catalog entry
        format
        {
        "naics_code":"test",
        "category":"11.0.1"
        }
        """

        try:

            industry_data = Industry.objects.get(
                naics_code=request.data['naics_code'])
            category_data = JobCategory.objects.get(
                o_net_soc_code=request.data['category'])
            data, __ = JobCatalog.objects.get_or_create(
                naics_code=industry_data, category=category_data)
            if __:
                message = "Catalog created"
            else:
                message = "Catalog already exists"

            return Response({"message": message},
                            status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": "{}".format(e)},
                            status=status.HTTP_400_BAD_REQUEST)

    def make_complex_query_set(self):
        """
        making complex queryset for filtering the job catalog

        :return:
        :rtype:
        """

        query = self.request.GET.get("q")
        category_name = self.request.GET.get("category_name")
        o_net_soc_code = self.request.GET.get("o_net_soc_code")
        description = self.request.GET.get("description")
        job_title = self.request.GET.get("job_title")
        level = self.request.GET.get("level", '')

        q_object = Q()

        if query:
            q_object.add((
                Q(category__category_name__icontains=query) |
                Q(category__o_net_soc_code__icontains=query) |
                Q(category__description__icontains=query) |
                Q(category__job_title__description__icontains=query) |
                Q(category__job_title__title__icontains=query)
            ), Q.OR)

            if query.isnumeric():
                q_object.add(
                    Q(category__job_title__level__icontains=int(query)), Q.OR)

        else:
            if category_name:
                q_object.add(
                    Q(category__category_name__icontains=category_name),
                    Q.AND)

            if o_net_soc_code:
                q_object.add(
                    Q(category__o_net_soc_code__icontains=o_net_soc_code),
                    Q.AND)

            if description:
                q_object.add((
                    Q(category__description__icontains=description) |
                    Q(
                        category__job_title__description__icontains=description)
                ), Q.AND)

            if job_title:
                q_object.add(
                    Q(category__job_title__title__icontains=job_title),
                    Q.AND)

            if level:
                if level.isnumeric():
                    q_object.add(
                        Q(category__job_title__level__icontains=int(level)),
                        Q.AND)
                else:
                    raise Exception(
                        ErrorMessage.WRONG_FIELD_TYPE.value.format("level",
                                                                   "numeric"))

        return q_object

    def make_order_by_combination(self):
        """
        make order by combinations for sorting job catalog

        :return:
        :rtype:
        """
        order_by_list = []
        order_by = self.request.GET.get("order_by", None)

        if order_by:
            order_by_list = [SORT_BY_REFERENCE_DICT[i.strip()]
                             for i in order_by.split(",")]

        return order_by_list


class JobCatalogDetailViewList(APIView):
    """
    JOb Catalog View for a specific record
    """

    authentication_classes = [RemoteJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        """
        Get a specific record of the JobCatalog

        :param pk:
        :type pk:
        :return:
        :rtype:
        """
        try:
            # x = category__job_title__program_id
            return JobCatalog.objects.get(Q(id=pk) | Q(uid=pk))
        except JobCatalog.DoesNotExist:
            raise Http404

    @swagger_auto_schema(
        operation_description=GET_SINGLE_JOB_CATALOG,
        responses={
            "200": "Success",
            "400": "Bad Request"
        }
    )
    def get(self, request, pk, format=None):
        """
        Method to list down details of a specific record of the system defined
        industry, system defined catgeory with job title forming unique set with
        job category, having status to be true with the help of the primary key
        provided in the requested url.
        Request samples:
            http://dev-awsnlb.simplifyvms.com:8002/job_catalog/ff8a7746-a8a7-4b99-9243-9dba0d2e1182

        :param request:
        :type request:
        :param pk:
        :type pk:
        :param format:
        :type format:
        :return:
        :rtype:
        """
        settings.LOGGER.info(
            "JobCatalogDetailViewList >> get >> request {}, pk: {}".format(
                request.GET, pk))
        try:
            program_id = request.META.get('HTTP_X_SVMS_PROGRAM_ID')
            catalog_obj = self.get_object(pk)
            context = {'program_id': program_id, "request_obj": self.request}
            serializer = JobCatalogSerializer(catalog_obj, context=context)
            settings.LOGGER.info(
                "JobCatalogDetailViewList >> get >> pk: {}, Response {}".format(
                    pk, serializer.data))
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        except Exception as e:
            settings.LOGGER.info(
                "JobCatalogDetailViewList >> get >> pk: {}, error {}".format(pk,
                                                                             e))
            return Response({"error": "{}".format(e)},
                            status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description=PUT_SINGLE_JOB_CATALOG,
        request_body=JobCatalogSerializer,
        responses={
            '202': "Accepted",
            '400': "Bad Request"
        }
    )
    def put(self, request, pk, format=None):
        """
        Method to update the job catalog entry with the help
        of primary key provided in the requested url.
        This method allows to update job level, job description,
        job tags etc,
        Note:
        Job Category and job title are not editable, you cannot
        update this fields.

        :param request:
        :type request:
        :param pk:
        :type pk:
        :param format:
        :type format:
        :return:
        :rtype:
        """
        settings.LOGGER.info(
            "JobCatalogDetailViewList >> PUT >> requset:{},  pk: {}".format(
                request.query_params, pk))

        try:
            program_id = request.META.get('HTTP_X_SVMS_PROGRAM_ID')
            if not program_id:
                settings.LOGGER.info(
                    "JobCatalogDetailViewList >> PUT >>  pk: {}, error:{} ".format(
                        pk, "Program Id not found"))
                return Response(
                    {"error": "Program Id not found"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if 'category' in request.data and 'job_title' in request.data[
                    'category']:
                job_title_data = request.data['category']['job_title']
                for data in job_title_data:
                    job_title_data_list = {}
                    for each_data in data:
                        if each_data in EDITABLE_FIELDS:
                            job_title_data_list.update(
                                {each_data: data[each_data]}
                            )
                            job_title_obj = JobTitleDetailView.get_object(
                                self, data['id'])

                    if job_title_obj.program_id != program_id:
                        settings.LOGGER.info(
                            "JobCatalogDetailViewList >> PUT >>  pk: {}, error:{} ".format(
                                pk, "Not authorized to edit"))
                        return Response(
                            {"error": "Not authorized to edit"},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    serializer = JobTitleSerializer(
                        instance=job_title_obj, data=job_title_data_list,
                        partial=True)
                    if serializer.is_valid():
                        serializer.save()
                    else:
                        settings.LOGGER.info(
                            "JobCatalogDetailViewList >> PUT >>  pk: {}, error:{} ".format(
                                pk,
                                "Only Job Level, Description and Job Tag is editable"))
                        return Response(
                            {
                                "error": "Only Job Level, Description and Job Tag is editable"},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    catalog_obj = self.get_object(pk)
                    serializer = JobCatalogSerializer(catalog_obj)
                    settings.LOGGER.info(
                        "JobCatalogDetailViewList >> PUT >>  pk: {}, Response:{} ".format(
                            pk, serializer.data))

                    return Response(
                        serializer.data,
                        status=status.HTTP_200_OK
                    )
        except Exception as e:
            settings.LOGGER.info(
                "JobCatalogDetailViewList >> PUT >>  pk: {}, error:{} ".format(
                    pk, e))
            return Response({"error": "{}".format(e)},
                            status=status.HTTP_400_BAD_REQUEST)

class CategoryTitleListView(
    viewsets.ModelViewSet
    ):
    """
    This view contains the list of all categories with o_net_soc_code,
    category name and description that is defined by the system and is not
    going to change very frequently.
    Description from this table will be used by the job title at first upon
    selecting the job category while creating job title.
    """
    authentication_classes = [RemoteJWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = JobsPagination
    http_method_names = ['get']
    serializer_class = JobCategoryTitleSerializer

    def get_queryset(self):
        try:
            q_object = self.make_complex_query_set()
            if q_object:
                obj = JobTitle.objects.filter(q_object).distinct()
            else:
                obj = JobTitle.objects.all()
            
            self.total_count = obj.count()
            return obj
            
        except JobTitle.DoesNotExist:
            raise Http404

    def get_paginated_response(self, data):
        
        res = {
                "total_count": self.total_count,
                "items_per_page":len(data),
                "data": data,
                "status": status.HTTP_200_OK
        }
       
        return Response(res)

    def make_complex_query_set(self):
        """
        function to search, filter and sort the job catalog with
        making complex queryset for filtering the job catalog

        :return:
        :rtype:
        """

        query = self.request.GET.get("q")
        category = self.request.GET.get("category")
        title = self.request.GET.get("title")

        q_object = Q()

        if query:
            q_object.add((
                Q(category__category_name__icontains=query) |
                Q(title__icontains=query) 
            ), Q.OR)

        else:
            if category:
                q_object.add(
                    Q(category=category),
                    Q.AND)
            if title:
                q_object.add(
                    Q(title__icontains=title),
                    Q.AND)

        return q_object



class CategoryIndustryListView(APIView):
    """This view is used to get list of industry in a category."""
    authentication_classes = [RemoteJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        o_net_soc_code = kwargs["o_net_soc_code"]

        if JobCategory.objects.filter(o_net_soc_code=o_net_soc_code):
            job_category_obj = JobCategory.objects.get(
                o_net_soc_code=o_net_soc_code)

            industry_data = list(JobCatalog.objects.filter(
                category=job_category_obj).annotate(
                industy_uid=F('naics_code__uid'),
                industy_naics_code=F('naics_code__naics_code'),
                industry_type=F('naics_code__industry_type')
                ).values('industy_uid', 'industy_naics_code', 'industry_type'
            ))
            return Response(industry_data)

        else:
            return Response("code not found", status=status.HTTP_404_NOT_FOUND)