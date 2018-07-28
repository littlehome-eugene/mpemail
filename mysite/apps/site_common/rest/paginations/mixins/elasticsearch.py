from django.utils import six
from django.core.paginator import InvalidPage, Paginator as DjangoPaginator

from rest_framework.exceptions import NotFound

from elasticsearch_dsl import Search


class ElasticsearchPaginationMixin(object):

    def paginate_queryset(self, queryset, request, view=None, **kwargs):
        """
        copied from rest_framework.pagination.PageNumberPagination
        """
        page_size = self.get_page_size(request)
        if not page_size:
            return None

        paginator = self.django_paginator_class(queryset, page_size)
        page_number = request.query_params.get(self.page_query_param, 1)
        if page_number in self.last_page_strings:
            page_number = paginator.num_pages

        try:
            self.page = paginator.page(page_number)
        except InvalidPage as exc:
            page_number = 1
            self.page = paginator.page(page_number)

            # msg = self.invalid_page_message.format(
            #     page_number=page_number, message=six.text_type(exc)
            # )
            # raise NotFound(msg)

        if paginator.count > 1 and self.template is not None:
            # The browsable API should display pagination controls.
            self.display_page_controls = True

        self.request = request

        if isinstance(self.page.object_list, Search):
            res = self.page.object_list.execute()
            hits = res.hits
            self.page.object_list = hits
        return list(self.page)
