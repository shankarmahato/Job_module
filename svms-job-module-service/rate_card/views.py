import operator
from functools import reduce

from django.conf import settings
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets, status, generics
from rest_framework.response import Response

from connectors.vms_profile_manager.auth import IsAuthenticated, \
    RemoteJWTAuthentication
from .models import RateCard, RateCardConfig
from .serializers import RateCardSerializer, RateCardConfigSerializer
from .utils import arrange_priority_search_keys_n_get_queryset


class RateCardViewSet(mixins.CreateModelMixin,
                      mixins.ListModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet,
                      ):
    """
    RateCard Create,  Retrieve, List
    """
    authentication_classes = [RemoteJWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = RateCard.objects.all()
    serializer_class = RateCardSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('job_category__id', 'job_title__id',
                     'job_level', 'job_template__id',
                     'hierarchy', 'work_location',
                     'region', 'currency',
                     'rates_of_rate_card__unit_of_measure',
                     'rates_of_rate_card__min_rate',
                     'rates_of_rate_card__max_rate',
                     'rates_of_rate_card__min_rate_rule',
                     'rates_of_rate_card__max_rate_rule',
                     'rates_of_rate_card__is_active')
    multiple_lookup_fields = (
        'program_id', 'pk')

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
            q_object = reduce(operator.and_, [Q(**{key: val}) for key, val in
                                              filter_fields.items()])

            queryset_result = queryset.filter(q_object)

            if queryset_result:
                queryset = queryset_result
            else:
                queryset = arrange_priority_search_keys_n_get_queryset(
                    self.kwargs["program_id"],
                    filter_fields, queryset)
        return queryset

    def get_list(self, request, program_id, *args, **kwargs):
        """
        get rate card records
        :param request:
        :type request:
        :param args:
        :type args:
        :param kwargs:
        :type kwargs:
        :return:
        :rtype:
        """
        try:
            settings.LOGGER.info(
                "RateCardViewSet >> get_list >> request: {}".format(
                    request.GET))
            # program_id_in_filter = program_id
            program_id_in_header = program_id

            # if program_id_in_filter:
            #     self.queryset = self.queryset.filter(
            #         Q(program_id=program_id_in_filter))
            total_records = self.queryset.count()

            if program_id_in_header:
                self.queryset = self.queryset.filter(
                    Q(program_id="0") | Q(program_id=program_id_in_header))

            response = self.list(request, *args, **kwargs)
            settings.LOGGER.info(
                "RateCardViewSet >> get_list >> response: {}".format(
                    response.status_code))

            response.data.update({"total_records": total_records,
                                  "items_per_page": request.query_params.get(
                                      "limit") or 10})

            return Response(response.data, status=status.HTTP_200_OK)

        except Exception as error:
            settings.LOGGER.error(
                "RateCardViewSet >> get_list >> error: {}".format(error))
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

        for field in self.multiple_lookup_fields:
            field_value = self.kwargs.get(field, None)
            if field_value:
                filter_kwargs.update({field: field_value})

        obj = get_object_or_404(queryset, **filter_kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj

    def get(self, request, *args, **kwargs):
        """
        get single rate card record
        :param request:
        :type request:
        :param args:
        :type args:
        :param kwargs:
        :type kwargs:
        :return:
        :rtype:
        """
        try:
            settings.LOGGER.info(
                "RateCardViewSet >> get >> request: {}".format(request.GET))
            response = self.retrieve(request, *args, **kwargs)
            settings.LOGGER.info(
                "RateCardViewSet >> get >> response: {}".format(response.data))
            return response
        except Exception as error:
            settings.LOGGER.error(
                "RateCardViewSet >> get >> error: {}".format(error))
            return Response({"error": "{}".format(error)},
                            status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):
        """
        create new rate card
        :param request:
        :type request:
        :param args:
        :type args:
        :param kwargs:
        :type kwargs:
        :return:
        :rtype:
        """
        request.data["program_id"] = str(kwargs["program_id"])
        try:
            settings.LOGGER.info(
                "RateCardViewSet >> post >> request: {}".format(request.data))
            response = self.create(request, *args, **kwargs)
            settings.LOGGER.info(
                "RateCardViewSet >> post >> response: {}".format(response.data))
            return response
        except Exception as error:
            settings.LOGGER.error(
                "RateCardViewSet >> post >> error: {}".format(error))
            return Response({"error": "{}".format(error)},
                            status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        """
        update rate card
        :param request:
        :type request:
        :param args:
        :type args:
        :param kwargs:
        :type kwargs:
        :return:
        :rtype:
        """
        try:
            settings.LOGGER.info(
                "RateCardViewSet >> put >> request: {}".format(request.data))
            response = self.update(request, *args, **kwargs)
            settings.LOGGER.info(
                "RateCardViewSet >> put >> response: {}".format(response.data))
            return response
        except Exception as error:
            settings.LOGGER.error(
                "RateCardViewSet >> put >> error: {}".format(error))
            return Response({"error": "{}".format(error)},
                            status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        """
        delete rate card
        :param request:
        :type request:
        :param args:
        :type args:
        :param kwargs:
        :type kwargs:
        :return:
        :rtype:
        """
        try:
            settings.LOGGER.info(
                "RateCardViewSet >> delete >> request: {}".format(request.path))
            response = self.destroy(request, *args, **kwargs)
            settings.LOGGER.info(
                "RateCardViewSet >> delete >> response: {}".format(
                    response.status_code))
            return response
        except Exception as error:
            settings.LOGGER.error(
                "RateCardViewSet >> delete >> error: {}".format(error))
            return Response({"error": "{}".format(error)},
                            status=status.HTTP_400_BAD_REQUEST)


class RateCardConfigList(mixins.ListModelMixin,
                         mixins.CreateModelMixin,
                         generics.GenericAPIView):
    authentication_classes = [RemoteJWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = RateCardConfig.objects.all()
    serializer_class = RateCardConfigSerializer
    multiple_lookup_fields = ('program_id', 'pk')

    def get_serializer_context(self):
        context = super(RateCardConfigList, self).get_serializer_context()
        context.update({'token': self.request.META.get("HTTP_AUTHORIZATION"),
                        'ua': self.request.META.get("HTTP_USER_AGENT"),
                        "user_id": self.request.user.id,
                        "request": self.request
                        })
        return context

    def filter_queryset(self, queryset):
        """
        Given a queryset, filter it with whichever filter backend is in use.

        You are unlikely to want to override this method, although you may need
        to call it either from a list view, or from a custom `get_object`
        method if you want to apply the configured filtering backend to the
        default queryset.
        """
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        queryset = queryset.select_related().filter(
            program_id=self.kwargs["program_id"])
        return queryset

    def get(self, request, *args, **kwargs):
        try:
            settings.LOGGER.info(
                "RateCardConfigList >> get >> request: {}".format(request.GET))
            res = self.list(request, *args, **kwargs)
            settings.LOGGER.info(
                "RateCardConfigList >> get >> response: {}".format(
                    res.status_code))
            return res
        except Exception as error:
            settings.LOGGER.error(
                "RateCardConfigList >> get >> error: {}".format(error))
            return Response({"error": "{}".format(error)},
                            status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):
        try:
            settings.LOGGER.info(
                "RateCardConfigList >> post >> request: {}".format(
                    request.data))
            request.data["program_id"] = str(kwargs["program_id"])
            res = self.create(request, *args, **kwargs)
            settings.LOGGER.info(
                "RateCardConfigList >> post >> response: {}".format(
                    res.data))
            return res
        except Exception as error:
            settings.LOGGER.info(
                "RateCardConfigList >> post >> error: {}".format(error))
            return Response({"error": "{}".format(error)},
                            status=status.HTTP_400_BAD_REQUEST)


class RateCardConfigDetail(mixins.RetrieveModelMixin,
                           mixins.UpdateModelMixin,
                           mixins.DestroyModelMixin,
                           generics.GenericAPIView):
    authentication_classes = [RemoteJWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = RateCardConfig.objects.all()
    serializer_class = RateCardConfigSerializer
    lookup_field = "program_id"

    def get_serializer_context(self):
        context = super(RateCardConfigDetail, self).get_serializer_context()
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
        try:
            settings.LOGGER.info(
                "RateCardConfigDetail >> get >> request: {}".format(
                    request.GET))
            res = self.retrieve(request, *args, **kwargs)
            settings.LOGGER.info(
                "RateCardConfigDetail >> get >> response: {}".format(
                    res.status_code))
            return res
        except Exception as error:
            settings.LOGGER.info(
                "RateCardConfigDetail >> get >> error: {}".format(error))
            return Response({"error": "{}".format(error)},
                            status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        try:
            settings.LOGGER.info(
                "RateCardConfigDetail >> put >> request: {}".format(
                    request.data))
            res = self.update(request, *args, **kwargs)
            settings.LOGGER.info(
                "RateCardConfigDetail >> put >> response: {}".format(
                    request.data))
            return res
        except Exception as error:
            settings.LOGGER.info(
                "RateCardConfigDetail >> put >> error: {}".format(error))
            return Response({"error": "{}".format(error)},
                            status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        try:
            settings.LOGGER.info(
                "RateCardConfigDetail >> delete >> request: {}".format(
                    request.path))
            res = self.destroy(request, *args, **kwargs)
            settings.LOGGER.info(
                "RateCardConfigDetail >> delete >> response: {}".format(
                    request.data))
            return res
        except Exception as error:
            settings.LOGGER.info(
                "RateCardConfigDetail >> delete >> error: {}".format(error))
            return Response({"error": "{}".format(error)},
                            status=status.HTTP_400_BAD_REQUEST)
