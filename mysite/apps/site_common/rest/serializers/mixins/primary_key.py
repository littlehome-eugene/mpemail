from rest_framework import serializers

from site_common.rest.serializers.primary_key import PrimaryKeyRelatedField


class PrimaryKeyModelSerializer(object):

    serializer_related_field = PrimaryKeyRelatedField
