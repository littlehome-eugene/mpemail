from rest_framework import serializers


class PrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):

    def to_representation(self, value):
        return super().to_representation(value)
    # def to_representation(self, value):
    #     if self.pk_field is not None:
    #         return self.pk_field.to_representation(value.pk)
    #     return {
    #         "id": value.pk
    #     }
