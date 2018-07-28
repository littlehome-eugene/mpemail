from django.conf.urls import url, include

urlpatterns = [
]

from site_common.rest.routers import NoFormatSuffixRouter
router = NoFormatSuffixRouter(trailing_slash=False)

from mpemail.rest.viewsets.email import EmailViewSet
router.register(r'email', EmailViewSet)

urlpatterns += [
    url(r'^rest_api/', include(router.urls)),
]
