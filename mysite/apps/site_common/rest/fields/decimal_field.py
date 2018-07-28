from django.core import validators
from django.core.exceptions import ValidationError
from django.utils.encoding import smart_text

from rest_framework import serializers

from decimal import Decimal, ROUND_DOWN
from decimal import Decimal, DecimalException


class MapDecimalField(serializers.DecimalField):

    def to_internal_value(self, value):
        if value in validators.EMPTY_VALUES:
            return None
        value = smart_text(value).strip()
        try:
            value = Decimal(value).quantize(Decimal('.000000000001'), rounding=ROUND_DOWN)
        except DecimalException:
            raise ValidationError(self.error_messages['invalid'])
        return value
