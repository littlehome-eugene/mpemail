from rest_framework import routers


class NoFormatSuffixRouter(routers.DefaultRouter):

    include_format_suffixes = False
