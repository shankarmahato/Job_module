from django.urls import path

from job_catalog import views
from .views import CategoryView
from rest_framework import routers

router = routers.SimpleRouter(trailing_slash=False)

app_name = 'catalog'


# URL for listing and creating notification
router.register(r'/category_title', views.CategoryTitleListView, basename='JobTitle')

urlpatterns = [
    path('', views.JobCatalogViewList.as_view(),
         name='catalog_list'),
    path(
        '<int:pk>',
        views.JobCatalogDetailViewList.as_view(),
        name='catalog_detail_list'
    ),
    path(
        '/<uuid:pk>',
        views.JobCatalogDetailViewList.as_view(),
        name='catalog_detail_list'
    ),
    path(
        '/industry',
        views.IndustryViewSet.as_view({'get': 'list'}),
        name='industry'
    ),
    path(
        '/industry/<int:pk>',
        views.IndustryViewSet.as_view({'get': 'retrieve'}),
        name='industry'
    ),
    path(
        '/industry/<uuid:uid>',
        views.IndustryViewSet.as_view({'get': 'get'}),
        name='industry'
    ),
    path('/import_industry', views.IndustryImportView.as_view(),
         name='import_industry'),
    path('/category', CategoryView.as_view(
        {'get': 'list'}), name='category_list'),
    path('category/<int:pk>',
         CategoryView.as_view({'get': 'retrieve'}), name='single_category'),
    path('/category/<uuid:uid>',
         CategoryView.as_view({'get': 'get'}), name='single_category'),
    path('/import_category', views.CategoryImportView.as_view(),
         name='import_category'),

    path('/job_title', views.JobTitleView.as_view(), name='job_title'),
    path('/job_title/<int:pk>', views.JobTitleDetailView.as_view(),
         name='job_title_detail'),
    path('/job_title/<uuid:pk>', views.JobTitleDetailView.as_view(),
         name='job_title_detail'),
    path(
        '/upload_job_title',
        views.JobTitleImportView.as_view(),
        name="upload_job_title"
    ),
    # path(
    #     '/category_title',
    #     views.CategoryTitleListView.as_view(),
    #     name="category_title"
    # ),
    path(
        "/category-industry-list/<str:o_net_soc_code>", 
        views.CategoryIndustryListView.as_view()
    )

]

urlpatterns += router.urls
