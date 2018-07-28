from django.conf import settings

from rest_framework import serializers

from site_common.utils.image.image_url import url_for_filefield


class ImageField(serializers.ImageField):

    def to_representation(self, value):
        return url_for_filefield(value)
