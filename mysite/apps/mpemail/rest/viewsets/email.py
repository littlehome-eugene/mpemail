import json

from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response

from mpemail.rest.serializers.email import EmailSerializer
from mpemail.models.email import Email
from pandas import ExcelWriter
import pandas as pd
import os
from django.conf import settings


columns_delivery = [
    '보내는분 성명',
    '보내는분 전화',
    '보내는분 핸드폰',
    '보내는분 우편번호',
    '보내는분 주소',
    '고객성명',
    '우편번호',
    '주소',
    '전화번호',
    '핸드폰번호',
    '택배박스 갯수',
    '운임Type',
    '주문번호',
    '품목',
    '배송메세지',
]


columns_order = [
    '일자',
    '순번',
    '거래처코드',
    '거래처명',
    '담당자',
    '출하창고',
    '거래유형',
    '통화',
    '환율',
    '전잔액',
    '현잔액',
    '품목코드',
    '품목명',
    '규격',
    '수량',
    '단가(vat포함)',
    '외화금액',
    '공급가액',
    '부가세',
    '적요',
    '부대비용',
    '생산전표생성',
    'Ecount',
]



class EmailViewSet(viewsets.ModelViewSet):

    queryset = Email.objects.all()

    serializer_class = EmailSerializer

    @list_route(methods=['post', 'put', 'patch'])
    def get_or_create_list(self, request, *args, **kwargs):

        data_all = request.data

        metadata = data_all.get('metadata')
        messages = data_all.get('messages')

        for k, v in metadata.items():

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
                    print(attachment.get('filename'), attachment.get('mimetype'))
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
        mids = request.data.get('mids')

        emails = Email.objects.eligible_for_order().filter(msg_mid__in=mids)

        df_delivery = pd.DataFrame(columns=columns_delivery)
        df_order = pd.DataFrame(columns=columns_order)

        result = {}

        for email in emails:

            try:
                res = email.process_order()
                df_delivery_1, df_order_1 = res

                email.auto_order_status = 'process_success'
                email.save()
                result[email.msg_mid] = {
                    'error': None,
                    'auto_order_status': email.auto_order_status,
                }
            except ValueError as e:
                error = str(e)
                email.auto_order_status = 'process_fail'
                email.save()

                result[email.msg_mid] = {
                    'error': error,
                    'auto_order_status': email.auto_order_status,
                }
                continue

            df_delivery = pd.concat([df_delivery, df_delivery_1], axis=0)
            df_order = pd.concat([df_order, df_order_1], axis=0)


        if result:
            writer = ExcelWriter(os.path.join(settings.OUTPUT_DIR, 'logistics.xlsx'))

            df_delivery.to_excel(
                writer,
                columns=columns_delivery
            )
            writer.save()

            writer = ExcelWriter(os.path.join(settings.OUTPUT_DIR, 'order.xlsx'))
            df_delivery.to_excel(
                writer,
                columns=columns_order
            )
            writer.save()

        return Response(result)