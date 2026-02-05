from .constants import PAGE_LIMIT
from rest_framework.pagination import PageNumberPagination


class LimitPageNumberPagination(PageNumberPagination):
    page_size = PAGE_LIMIT
    page_size_query_param = 'limit'
