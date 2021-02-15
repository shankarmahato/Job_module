from django.urls import path

from . import views

app_name = 'rate_card'

urlpatterns = [
    path(
        '',
        views.RateCardViewSet.as_view({'get': 'get_list',
                                       'post': 'post'}),
        name='rate_card_get_list_n_post'
    ),
    path(
        '/<int:pk>',
        views.RateCardViewSet.as_view(
            {'get': 'get', 'put': 'put', 'delete': 'delete'}),
        name='rate_card_get_put_del'
    ),
    path('/config', views.RateCardConfigList.as_view()),
    path('/config/details', views.RateCardConfigDetail.as_view()),
]
