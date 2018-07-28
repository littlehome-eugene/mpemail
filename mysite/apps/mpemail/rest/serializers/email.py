from rest_framework import serializers

from mpemail.models.email import Email


class EmailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Email

        fields = [
            'id',
            'msg_id',
            'title',
            'sender',
            'has_attachment',
        ]
