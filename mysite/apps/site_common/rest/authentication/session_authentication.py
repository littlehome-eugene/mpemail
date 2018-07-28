from rest_framework.authentication import SessionAuthentication as OriginalSessionAuthentication
from rest_framework.authentication import BaseAuthentication
import logging
logger = logging.getLogger(__name__)


class SessionAuthenticationNoCsrf(OriginalSessionAuthentication):

    def authenticate(self, request):

        return super().authenticate(request)

    def enforce_csrf(self, request):
        return


class EmptyAuthentication(BaseAuthentication):
    def authenticate(self, request):

        user = getattr(request._request, 'user', None)
        return (user, None)
