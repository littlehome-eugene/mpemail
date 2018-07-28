import json

from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response

from mpemail.rest.serializers.email import EmailSerializer
from mpemail.models.email import Email


class EmailViewSet(viewsets.ModelViewSet):

    queryset = Email.objects.all()

    serializer_class = EmailSerializer

    @list_route(methods=['post', 'put', 'patch'])
    def get_or_create_list(self, request, *args, **kwargs):

        data_all = request.data

        metadata = data_all.get('metadata')
        messages = data_all.get('messages')

        for k, v in metadata.iteritems():

            msg_id = v['id']
            msg_mid = v['mid']
            message = messages.get(k)
            if not message:
                continue

            excel_attachment_count = 0
            attachment_count = 0
            attachments = message.get('attachments')

            if attachments:
                for attachment in attachments:
                    if attachment.get('mimetype') in Email.ALLOWED_EXCEL_MIME_TYPES:
                        excel_attachment_count += 1
                        attachment_count = attachment.get('count')

            body_text = ''

            if message['text_parts']:
                body_text = message['text_parts'][0]['data']
            data = {
                'title': v['subject'],
                'sender': v['from']['address'],
                'excel_attachment_count': excel_attachment_count,
                'attachment_count': attachment_count,
                'msg_mid': msg_mid,
                'body_text': body_text,
                'metadata': json.dumps(metadata[k], ensure_ascii=False),
                'messagedata': json.dumps(messages[k], ensure_ascii=False),
            }

            Email.objects.update_or_create(
                msg_id=msg_id,
                defaults=data
            )

        return Response([])


    @list_route(methods=['post', 'put', 'patch'])
    def order(self, request, *args, **kwargs):

        emails = Email.objects.eligible_for_order()

        for email in emails:
            email.process_order()

        return Response([])