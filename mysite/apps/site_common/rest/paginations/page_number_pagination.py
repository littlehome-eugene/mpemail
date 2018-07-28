# -*- coding: utf-8 -*-

from django.core.paginator import InvalidPage, Paginator as DjangoPaginator
from django.utils import six

from rest_framework.exceptions import NotFound
from collections import OrderedDict
from rest_framework import pagination
from rest_framework.response import Response


class PageNumberPagination(pagination.PageNumberPagination):
    def get_paginated_response(self, data):
        return Response(self.get_paginated_results(data))

    def get_paginated_results(self, data):

        return OrderedDict([
            ('count', self.page.paginator.count),
            ('paginate_by', self.get_page_size(self.request)),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data),
            ('page_number', self.page.number),
        ])

    @property
    def preset_page_number(self):
        if not hasattr(self, '_preset_page_number'):
            return None
        return self._preset_page_number

    @preset_page_number.setter
    def preset_page_number(self, value):
        self._preset_page_number = value

    def paginate_queryset(self, queryset, request, view=None):
        """
        Paginate a queryset if required, either returning a
        page object, or `None` if pagination is not configured for this view.
        """
        page_size = self.get_page_size(request)
        if not page_size:
            return None

        paginator = self.django_paginator_class(queryset, page_size)

        last_page_number = paginator.num_pages
        page_number = self.get_page_number(request, last_page_number)

        try:
            self.page = paginator.page(page_number)
        except InvalidPage as exc:
            msg = self.invalid_page_message.format(
                page_number=page_number, message=six.text_type(exc)
            )
            raise NotFound(msg)

        if paginator.num_pages > 1 and self.template is not None:
            # The browsable API should display pagination controls.
            self.display_page_controls = True

        self.request = request
        return list(self.page)

    def get_page_number(self, request, last_page_number):

        page_number = self.preset_page_number  # added
        if page_number is None:
            page_number = request.query_params.get(self.page_query_param, 1)

        if page_number in self.last_page_strings:
            page_number = last_page_number

        return page_number
