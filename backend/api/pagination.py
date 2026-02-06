from rest_framework.pagination import PageNumberPagination

from .constants import PAGE_LIMIT


class LimitPageNumberPagination(PageNumberPagination):
    page_size = PAGE_LIMIT
    page_size_query_param = 'limit'
