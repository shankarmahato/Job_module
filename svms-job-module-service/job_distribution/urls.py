from django.urls import path

from . import views

app_name = 'job_distribution'

urlpatterns = [
    path(
        '',
        views.VendorJobMappingViewSet.as_view(
            {'get': 'get_list', 'post': 'post'}),
        name='vendor_job__get_list'
    ),
    path(
        '/<int:pk>',
        views.VendorJobMappingViewSet.as_view(
            {'get': 'get', 'put': 'put', 'delete': 'delete'}),
        name='vendor_job__get_put_del'
    ),

    path(
        '/<uuid:vendor_id>/<str:job_id>',
        views.VendorJobMappingViewSet.as_view(
            {'put': 'opt_in_opt_out'}),
        name='vendor_job_patch'
    ),
    path(
        '/schedule_job',
        views.ScheduleJobVendorMappingViewSet.as_view(
            {'get': 'get_list'}),
        name='schedule_job__get_list'
    ),
    path(
        '/schedule_job/<int:pk>',
        views.ScheduleJobVendorMappingViewSet.as_view(
            {'get': 'get'}),
        name='schedule_job__get'
    ),

]
