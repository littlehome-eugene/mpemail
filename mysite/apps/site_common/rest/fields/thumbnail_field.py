import six
from site_common.utils.image import thumbor_url
from rest_framework import serializers


class ThumbnailField(serializers.CharField):

    def __init__(self, size_str='350x350', **kwargs):
        self.size_str = size_str
        super().__init__(**kwargs)

    def to_representation(self, value):

        if not value:
            return None

        if isinstance(value, six.string_types):
            original_url = value
        else:
            original_url = getattr(value, 'url', None)

        return thumbor_url(original_url, self.size_str)
