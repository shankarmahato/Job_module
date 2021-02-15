# from django.urls import path, include
from django.contrib import admin
from job import views
from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework_simplejwt import views as jwt_views
from django.conf.urls.static import static
from django.conf import settings

app_name = 'job'

schema_view = get_schema_view(
    openapi.Info(
        title="Job API",
        default_version='v1',
        description="Job Module",
        terms_of_service=settings.TERM_OF_SERVICE,
        contact=openapi.Contact(email="contact@ustech.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path('<str:program_id>/copyjob/<str:uid>', views.CopyJob.as_view(), name='copyjob'),
    path('<str:program_id>/job', views.JobView.as_view(), name='joblist'),
    path('<str:program_id>/job/<str:uid>',
         views.JobView.as_view(), name='detailjob'),
#     path('configuration', views.ConfigurationView.as_view(), name='configuration'),
    path('<str:program_id>/recent_job', views.RecentJob.as_view(), name="recent"),
    path('<str:program_id>/unique_template_name', views.UniqueTemplateName.as_view(), name="uniquetemp"),
    path('<str:program_id>/recent_job/<str:uid>', views.RecentJob.as_view(), name="recent"),
    path('<str:program_id>/draft_job', views.DraftJob.as_view(), name="draft"),
    path('<str:program_id>/draft_job/<str:uid>', views.DraftJob.as_view(), name="draft"),
    path('<str:program_id>/popular_job',
         views.PopularJob.as_view(), name="popularJob"),
     path('<str:program_id>/popular_job/<str:uid>',
         views.PopularJob.as_view(), name="popularJob"),
    path('<str:program_id>/job_template',
         views.JobTemplateView.as_view(), name="jobtemplate"),
    path('<str:program_id>/job_template/<str:uid>',
         views.JobTemplateView.as_view(), name="jobtemplatedetail"),
    path('<str:program_id>/job_approval/<int:pk>',
         views.JobApprovalView.as_view(), name="jobapproval"),
   
    path('talentneuron', views.TalentNeuronView.as_view({'get': 'list'}), name='talentneuron')
]
