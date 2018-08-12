import json
import datetime
import time
import requests

from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from django.db.models import F
from mpemail.rest.serializers.email import EmailSerializer
from mpemail.models.email import Email
from pandas import ExcelWriter
import pandas as pd
import os
from django.conf import settings
from urllib.parse import urlparse, urlunparse, urljoin, parse_qsl, ParseResult, unquote


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
                'sender_name': v['from']['fn'],
                'timestamp': v['timestamp'],
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

        import pdb; pdb.set_trace()
        mids = request.data.get('mids')
        if mids is None:
            mids = request._request.POST.get('mids')

        emails = Email.objects.eligible_for_order().filter(msg_mid__in=mids)

        eligible_mids = [e.msg_mid for e in emails]

        ineligible_mids = set(mids) - set(eligible_mids)
        ineligible_emails = Email.objects.filter(msg_mid__in=ineligible_mids)

        df_delivery = pd.DataFrame(columns=columns_delivery)
        df_order = pd.DataFrame(columns=columns_order)

        result = {}

        for email in ineligible_emails:
            result[email.msg_mid] = {
                'error': email.auto_order_error,
                'auto_order_status': email.auto_order_status
            }

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
                path = os.path.join(settings.DATA_DIR, time.strftime("%Y/%m/%d"))
                os.makedirs(path, exist_ok=True)

                path = os.path.join(path, '{}.csv'.format(email.id))
                df_delivery_1.to_csv(path_or_buf=path)

                email.order_data_path = path
                email.save()

            except ValueError as e:
                error = str(e)
                email.auto_order_status = 'process_fail'
                email.auto_order_error = error
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

            # for test
            df_delivery.to_csv(
                os.path.join(settings.OUTPUT_DIR, 'logistics.csv'),
                columns=columns_delivery
            )

            writer = ExcelWriter(os.path.join(settings.OUTPUT_DIR, 'order.xlsx'))
            df_delivery.to_excel(
                writer,
                columns=columns_order
            )
            writer.save()

        return Response(result)


    @list_route(methods=['post'])
    def status(self, request, *args, **kwargs):

        mids = request.data.get('mids')

        emails = Email.objects.filter(msg_mid__in=mids)

        result = emails.status()

        return Response(result)


    @list_route(methods=['post'])
    def order_complete(self, request, *args, **kwargs):

        mids = request.data.get('mids')

        emails = Email.objects.filter(msg_mid__in=mids).filter(
            auto_order_status='process_success'
        )

        emails.update(auto_order_status='complete')

        emails = Email.objects.filter(msg_mid__in=mids)
        result = emails.status()

        path = os.path.join(settings.OUTPUT_DIR, time.strftime("%Y/%m/%d"))
        os.makedirs(path, exist_ok=True)

        os.rename(
            os.path.join(settings.OUTPUT_DIR, 'logistics.xlsx'),
            os.path.join(path, 'logistics.xlsx')
        )

        os.rename(
            os.path.join(settings.OUTPUT_DIR, 'order.xlsx'),
            os.path.join(path, 'order.xlsx')
        )

        return Response(result)

    @list_route(methods=['post'])
    def manual_order_toggle(self, request, *args, **kwargs):

        mid = request.data.get('mid')
        email = Email.objects.get(msg_mid=mid)

        if email.manual_order_status == 'initial':
            email.manual_order_status = 'complete'
        else:
            email.manual_order_status = 'initial'

        email.save()

        emails = Email.objects.filter(id=email.id)

        result = emails.status()

        return Response(result)

    @list_route(methods=['post'])
    def manual_reply_toggle(self, request, *args, **kwargs):

        mid = request.data.get('mid')
        email = Email.objects.get(msg_mid=mid)

        if email.manual_reply_status == 'initial':
            email.manual_reply_status = 'complete'
        else:
            email.manual_reply_status = 'initial'

        email.save()

        emails = Email.objects.filter(id=email.id)

        result = emails.status()

        return Response(result)

    @list_route(methods=['post'])
    def reply(self, request, *args, **kwargs):
        from mpemail.logistics import get_logistics_info

        mids = request.data.get('mids')

        emails = Email.objects.filter(msg_mid__in=mids).filter(
            auto_order_status='complete',
            auto_reply_status__in=['initial', 'process_fail']
        ).order_by('timestamp')

        email = emails.first()

        start_date = None
        end_date = datetime.datetime.today().strftime('%Y%m%d')
        if email:
            start_date = datetime.datetime.fromtimestamp(
                int(email.timestamp)
            ).strftime('%Y%m%d')
        else:
            return Response({})

        logistics_data = get_logistics_info(start_date, end_date)
        df_logistics = pd.DataFrame(logistics_data)

        from_ = '{} {}'.format(
            settings.EMAIL_SENDER_NAME, settings.EMAIL_SENDER
        )
        cc = ''
        encryption = ''
        bcc = ''
        attach_pgp_pubkey = 'no'

        url = '/api/0/message/update/send/'
        url = urljoin(settings.MAILPILE_URL, url)

        for email in emails:
            email.prepare_reply(df_logistics)

            body = email.reply_html
            to = email.sender
            subject = 'Re: {}'.format(email.title)

            data = {
                'body': body,
                'from': from_,
                'cc': cc,
                'encryption': encryption,
                'mid': email.msg_mid,
                'bcc': '',
                'to': to,
                'attach-pgp-pubkey': 'no',
                'subject': subject
            }

            import pdb; pdb.set_trace()
            r = requests.post(
                url,
                json=data
            )