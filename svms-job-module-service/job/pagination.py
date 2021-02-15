from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class JobsPagination(PageNumberPagination):
    # page_size = 25
    page_size_query_param = 'limit'
    page_query_param = "page"
    # page_size_query_param = "items"
    max_page_size = 100
    last_page_strings = ("endpage",)


