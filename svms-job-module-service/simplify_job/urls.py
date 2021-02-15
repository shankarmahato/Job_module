"""simplifyai_job URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework_simplejwt import views as jwt_views
from django.conf.urls.static import static
from django.conf import settings
schema_view = get_schema_view(
    openapi.Info(
        title="Job API",
        default_version='v1',
        description="Job Module",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@ustech.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)
admin.site.site_header = "Simplify job Admin"
admin.site.site_title = "Simplify Job Admin Portal"
admin.site.index_title = "Welcome to Simplify Job Portal"
urlpatterns = [
    path('job-manager/health-check', include('healthcheck.urls')),
    path('job-manager/admin', admin.site.urls),
    path("job-manager/", include('job.urls', namespace='v1')),
    path("job-manager/job_catalog", include('job_catalog.urls')),
    path("job-manager/<program_id>/rate_cards", include('rate_card.urls')),
    path("job-manager/<program_id>/job_distribution",
         include('job_distribution.urls')),
    re_path(r'job-manager/swagger(?P<format>\.json|\.yaml)$',
            schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'job-manager/swagger/$', schema_view.with_ui('swagger',
                                                          cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'job-manager/redoc/$', schema_view.with_ui('redoc',
                                                        cache_timeout=0), name='schema-redoc'),
    path('job-manager/api/token/', jwt_views.TokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('job-manager/api/token/refresh/', jwt_views.TokenRefreshView.as_view(),
         name='token_refresh'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
# urlpatterns += [re_path(r'job-manage/silk/', include('silk.urls', namespace='silk'))]
