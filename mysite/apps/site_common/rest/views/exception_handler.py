try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

from rest_framework.views import exception_handler
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from rest_framework import status
from rest_framework.response import Response

from site_common.utils import url_utils


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    if isinstance(exc, ValidationError) or isinstance(exc, IntegrityError):
        data = {
            'errors': str(exc)
        }
        response = Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return response



# from saleor.seller.rest.exceptions.permission_denied import IsSellerPermissionDenied


# def custom_exception_handler(exc, context):
#     # Call REST framework's default exception handler first,
#     # to get the standard error response.
#     response = exception_handler(exc, context)

#     if isinstance(exc, IsSellerPermissionDenied):
#         request = context.get('request')
#         query = urlencode({
#             'next': request.META['HTTP_REFERER']
#         })

#         path = reverse('seller_admin:login')
#         redirect_url = url_utils.url(path=path, query=query)

#         response['REDIRECT_LOCATION'] = redirect_url

#         # this works with chrome as well
#         # response['REDIRECT_LOCATION'] = redirect_with_params('seller_admin:login', params={
#         #     'next': request.META['HTTP_REFERER']
#         # })

#     return response
