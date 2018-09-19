# -*- coding: utf-8 -*-
import os
import re
from django.db import models
from django.db.models import F

from urllib.parse import urljoin
from django.conf import settings
from django.db.models.query import QuerySet
import pandas as pd
import uuid
from pandas import ExcelWriter


product_excel = os.path.join(settings.PROJECT_DIR, 'apps/mpemail/config/product.xlsx')
df_product = pd.read_excel(product_excel)

keyword_title_excel = os.path.join(settings.PROJECT_DIR, 'apps/mpemail/config/keyword-title.xlsx')
df_keyword = pd.read_excel(keyword_title_excel)

company_excel = os.path.join(settings.PROJECT_DIR, 'apps/mpemail/config/company.xlsx')
df_company = pd.read_excel(company_excel, dtype=str)

include_title_path = os.path.join(settings.PROJECT_DIR, 'apps/mpemail/config/include-title.txt')

import codecs
with codecs.open(include_title_path,'r', encoding='EUC-KR') as f:
    include_titles = f.readlines()

include_titles = [x.strip() for x in include_titles]


exclude_keyword_path = os.path.join(settings.PROJECT_DIR, 'apps/mpemail/config/exclude-keyword.txt')

with codecs.open(exclude_keyword_path,'r', encoding='EUC-KR') as f:
    exclude_keywords = f.readlines()

exclude_keywords = [x.strip() for x in exclude_keywords]


class EmailQuerySet(QuerySet):

    def eligible_for_order(self):

        queryset = self

        queryset = queryset.filter(
            eligible_for_process=True,
            # for test
        # ).filter(
        #     auto_order_status__in=['initial', 'process_fail']
        )
        return queryset

    def status(self):
        queryset = self
        # queryset = Email.objects.filter(id__in=queryset.values_list('id', flat=True))
        values = queryset.annotate(
            mid=F('msg_mid'),
            error=F('auto_order_error')
        ).values(
            'mid',
            'auto_order_status',
            'auto_reply_status',
            'manual_order_status',
            'manual_reply_status',
            'error',
            'auto_reply_error',
        )

        result = {}
        for v in values:
            mid = v.pop('mid')
            result[mid] = v

        return result


class EmailManager(models.Manager):

    pass


class Email(models.Model):

    ALLOWED_EXCEL_MIME_TYPES = [
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/octet-stream',
    ]

    AUTO_STATUS = [
        ['initial', 'initial'],
        ['process_success', 'process_success'],
        ['process_fail', 'process_fail'],
        ['complete', 'complete'],
    ]

    MANUAL_STATUS = [
        ['initial', 'initial'],
        ['complete', 'complete'],
    ]

    # email data
    msg_mid = models.CharField(max_length=128, blank=True, db_index=True)
    msg_id = models.CharField(max_length=128, blank=True, db_index=True)
    title = models.CharField(max_length=2048, blank=True, db_index=True)
    sender = models.CharField(max_length=128, blank=True, db_index=True)
    sender_name = models.CharField(max_length=128, blank=True, default="")

    excel_attachment_count = models.IntegerField(default=0)
    body_text = models.TextField(default='')
    # attachment = models.FileField(upload_to='attachment/%Y/%m/%d/', null=True)
    # attachment_count = models.IntegerField(default=0)  # this is used in part-{attachment_count}
    # email data

    eligible_for_process = models.BooleanField(default=False, db_index=True)
    auto_order_error = models.CharField(max_length=128, blank=True, default="")
    auto_reply_error = models.CharField(max_length=128, blank=True, default="")
    timestamp = models.IntegerField(default=0, db_index=True)

    # status
    auto_order_status = models.CharField(max_length=16, choices=AUTO_STATUS, default='initial')
    auto_reply_status = models.CharField(max_length=16, choices=AUTO_STATUS, default='initial')
    manual_order_status = models.CharField(max_length=16, choices=MANUAL_STATUS, default='initial')
    manual_reply_status = models.CharField(max_length=16, choices=MANUAL_STATUS, default='initial')
    # status

    # meta data
    metadata = models.TextField(default='')
    messagedata = models.TextField(default='')
    created_at = models.DateTimeField(auto_now_add=True)
    # meta data

    # order_data_path = models.CharField(max_length=256, default="", blank=True)
    # reply_html = models.TextField(default='')

    objects = EmailManager.from_queryset(EmailQuerySet)()


    def check_eligible_for_process(self):

        email = self

        # if email.excel_attachment_count == 0:
        #     email.auto_order_error = '첨부파일이 없음'
        #     return False

        df_seller = df_company.loc[df_company['email'].str.contains(email.sender)]
        if df_seller.empty:

            email.auto_order_error = '판매자를 찾을 수 없음'
            return False

        found = False
        for i, title in enumerate(include_titles):
            if email.title.startswith(title):
                found = True
                break
        if not found:
            email.auto_order_error = '이메일 제목'
            return False

        found = False
        for i, keyword in enumerate(exclude_keywords):
            if keyword in email.body_text or keyword in email.title:
                found = True
                break
        if found:
            email.auto_order_error = '제외어가 포함되어 있음'
            return False

        return True

    # def attachment_download_url(self):

    #     email = self

    #     url = '/message/download/get/={mid}/part-{count}/'.format(
    #         mid=email.msg_mid,
    #         count=email.attachment_count
    #     )

    #     url = urljoin(settings.MAILPILE_URL, url)

    #     return url

    def process_attachment(self, attachment):

        error = None
        email = self
        process_order_fail_reason = None

        try:
            df = pd.read_excel(attachment.attachment, dtype=str)
            df.replace('nan', '', inplace=True)
        except:
            email.attachments.all().delete()
            email.save()
            raise ValueError("첨부파일 파싱 오류")

        df.columns = df.columns.str.strip()

        df_seller = df_company.loc[df_company['email'].str.contains(email.sender)]
        if df_seller.empty:
            raise ValueError('판매자 못찾음')
        seller_dict = df_seller.iloc[0].to_dict()

        product = df_keyword['품목']
        count = df_keyword['수량']

        product_column = None
        count_column = None

        customer = df_keyword['고객성명']
        postal = df_keyword['우편번호']
        address = df_keyword['주소']
        address_detail = df_keyword['상세주소']
        phone = df_keyword['전화번호']
        message = df_keyword['배송메시지']
        cellphone = df_keyword['핸드폰']

        customer_column = None
        postal_column = None
        address_column = None
        address_detail_column = None
        phone_column = None
        message_column = None
        cellphone_column = None

        sender = df_keyword['보내는이']
        sender_phone = df_keyword['보내는이전화번호']
        sender_cellphone = df_keyword['보내는이핸드폰']

        sender_column = None
        sender_phone_column = None
        sender_cellphone_column = None

        order_list = []
        for column in df.columns:
            column_w = xstr(column)
            if column_w in [xstr(a) for a in product.dropna().tolist()]:
                product_column = column
            elif column_w in [xstr(a) for a in count.dropna().tolist()]:
                count_column = column
            elif column_w in [xstr(a) for a in customer.dropna().tolist()]:
                customer_column = column
            elif column_w in [xstr(a) for a in postal.dropna().tolist()]:
                postal_column = column
            elif column_w in [xstr(a) for a in address.dropna().tolist()]:
                address_column = column
            elif column_w in [xstr(a) for a in address_detail.dropna().tolist()]:
                address_detail_column = column
            elif column_w in [xstr(a) for a in phone.dropna().tolist()]:
                phone_column = column
            elif column_w in [xstr(a) for a in message.dropna().tolist()]:
                message_column = column
            elif column_w in [xstr(a) for a in sender.dropna().tolist()]:
                sender_column = column
            elif column_w in [xstr(a) for a in sender_phone.dropna().tolist()]:
                sender_phone_column = column
            elif column_w in [xstr(a) for a in sender_cellphone.dropna().tolist()]:
                sender_cellphone_column = column
            elif column_w in [xstr(a) for a in cellphone.dropna().tolist()]:
                cellphone_column = column

        if product_column is None:
            raise ValueError('품목 없음')
        if customer_column is None:
            error = '고객성명 없음'
            raise ValueError(error)
        if address_column is None:
            error = '주소 없음'
            raise ValueError(error)
        if phone_column is None:
            error = '전화번호 없음'
            raise ValueError(error)

        for index, row in df.iterrows():

            if not row[product_column]:
                raise ValueError('품목 없음')
            if not row[customer_column]:
                error = '고객성명 없음'
                raise ValueError(error)
            if not row[address_column]:
                error = '주소 없음'
                raise ValueError(error)
            if not row[phone_column]:
                error = '전화번호 없음'
                raise ValueError(error)

            products = row[product_column].split('//')
            count_by_countcolumn = row.get(count_column) or None
            if count_by_countcolumn is not None:
                count_by_countcolumn = int(count_by_countcolumn)
            count_sum = 0

            if sender_column:
                sender = row[sender_column]
            else:
                sender = None

            sender_phone = seller_dict['전화']
            sender_cellphone = seller_dict['핸드폰']


            customer = row[customer_column]
            if sender:
                if sender != seller_dict['거래처명']:
                    if sender != row[customer_column]:
                        customer = '{} ({})'.format(customer, sender)

            order_dict = {
                '고객성명': customer,
                '우편번호': str(row.get(postal_column) or ""),
                '주소': ' '.join([
                    str(row.get(address_column, '')),
                    str(row.get(address_detail_column, '')),
                ]),
                '전화번호': str(row[phone_column] or ""),
                '배송메세지': [row.get(message_column) or ''],
                '핸드폰번호': str(row.get(cellphone_column) or ""),

                '보내는분 성명': seller_dict['거래처명'],
                '보내는분 전화': str(sender_phone or ""),
                '보내는분 핸드폰': str(sender_cellphone or ""),
                '보내는분 우편번호': seller_dict['우편번호'],
                '보내는분 주소': seller_dict['주소'],

                '택배박스 갯수': '',
                '운임Type': '',
                '주문번호': 'o' + str(uuid.uuid4()),

            }

            for product in products:
                count_none = False
                productcode_count_pairs_bogus = re.findall('[^[]+\[([^]]+)\][^\d[]*(?:(\d)\s*[^개\d]+)?', product.strip())
                if productcode_count_pairs_bogus:
                    if productcode_count_pairs_bogus[0][1]:
                        error = '수량 파싱 실패 {}'.format(index)
                        raise ValueError(error)

                productcode_count_pairs = re.findall('[^[]+\[([^]]+)\][^\d[]*(?:(\d)\s*개)?', product.strip())
                if len(productcode_count_pairs) == 1:

                    product_code = productcode_count_pairs[0][0].strip()
                    count = productcode_count_pairs[0][1] or None
                    if count is None:
                        count_none = True
                        count = 1
                    count = int(count)
                    count_sum += count
                else:

                    error = '품목코드 파싱 실패 {}'.format(index)
                    raise ValueError(error)

                order_dict.setdefault('품목코드', [])
                order_dict['품목코드'].append(product_code)
                order_dict['품목코드_flat'] = product_code

                product = df_product.loc[df_product['품목코드']==product_code]
                if product.empty:
                    raise ValueError('상품 정보 없음 {}'.format(index))

                remaining = product.iloc[0]['재고 여부']
                if int(remaining) == 0:
                    raise ValueError('재고 없음 {}'.format(index))

                product_name = product.iloc[0]['품목명']
                order_dict.setdefault('품목', [])
                order_dict['품목'].append(product_name)
                order_dict['품목_flat'] = product_name

                order_dict.setdefault('수량', [])

                if count_none:
                    if count_by_countcolumn:
                        count = count_by_countcolumn

                order_dict['수량'].append(count)
                order_dict['수량_flat'] = count

                order_dict.setdefault('카톤', [])
                caton = product.iloc[0]['카톤수']
                try:
                    int(caton)
                except Exception as e:
                    raise ValueError("카톤수가 숫자가 아님 {}".format(index))
                order_dict['카톤'].append(caton)

            order_list.append(order_dict)


            if not count_none and count_by_countcolumn and count_by_countcolumn != count_sum:

                error = '수량 column 과 sum 이 다름 {}'.format(index)
                order_list.pop()

                raise ValueError(error)


        # place same address rows together

        df_delivery = pd.DataFrame(order_list)

        df_order = df_delivery[['수량_flat', '품목코드_flat']].copy()

        df_order = df_order.rename(columns={
            '수량_flat':'수량',
            '품목코드_flat':'품목코드',
        })

        df_order = df_order.groupby('품목코드').agg({'수량':'sum'}).reset_index()

        df_order['품목'] = ''
        df_order['거래처코드'] = seller_dict['거래처코드']
        df_order['거래처명'] = seller_dict['거래처명']
        df_order['담당자'] = ''
        df_order['출하창고'] = 100
        df_order['거래유형'] = seller_dict['거래유형코드']
        df_order['통화'] = ''
        df_order['환율'] = ''
        df_order['전잔액'] = ''
        df_order['현잔액'] = ''
        df_order['품목명'] = ''

        def dim(row):

            dim = df_product.loc[df_product['품목코드']==row['품목코드']]['규격'].iloc[0]
            return dim

        df_order['규격'] = df_order.apply(dim, axis=1)


        def price(row):
            price = df_product.loc[df_product['품목코드']==row['품목코드']][seller_dict['거래처코드']].iloc[0]
            return price


        df_order['단가(vat포함)'] = df_order.apply(price, axis=1)

        df_order['외화금액'] = ''

        def price_total(row):
            return int(row['단가(vat포함)'] * row['수량'] * 10 /11)
        df_order['공급가액'] = df_order.apply(price_total, axis=1)

        def tax(row):
            return row['단가(vat포함)'] * row['수량'] - row['공급가액']

        df_order['부가세'] = df_order.apply(tax, axis=1)

        df_order['적요'] = attachment.attachment.name.split('/')[-1]
        df_order['부대비용'] = ''
        df_order['생상전표생성'] = ''
        df_order['Ecount'] = 'Ecount'


        df_delivery = sort_by_column(df_delivery, '주소')

        row_prev = None
        index_prev = None
        df_delivery['to_be_deleted'] = False
        same = True
        for index, row in df_delivery.iterrows():
            if row_prev is not None:
                cols_compare = ['고객성명', '주소', '전화번호', '핸드폰번호']
                same = True
                for i, col_name in enumerate(cols_compare):
                    if row[col_name] != row_prev[col_name]:
                        same = False
                        break
                if same:
                    df_delivery.loc[index_prev, '품목'].extend(
                         df_delivery.loc[index, '품목']
                    )
                    df_delivery.loc[index_prev, '품목코드'].extend(
                         df_delivery.loc[index, '품목코드']
                    )
                    df_delivery.loc[index_prev, '수량'].extend(
                         df_delivery.loc[index, '수량']
                    )
                    df_delivery.loc[index_prev, '배송메세지'].extend(
                         df_delivery.loc[index, '배송메세지']
                    )
                    df_delivery.loc[index_prev, '카톤'].extend(
                         df_delivery.loc[index, '카톤']
                    )

                    df_delivery.loc[index, 'to_be_deleted'] = True
                else:
                    row_prev = row
                    index_prev = index
            else:
                row_prev = row
                index_prev = index

        df_delivery = df_delivery[df_delivery['to_be_deleted'] != True]

        def yellow(row):

            if len(row['품목']) > 1:
                return True

            for caton, count in zip(row['카톤'], row['수량']):
                if int(count) > int(caton):
                    return True

            return False

        df_delivery['yellow'] = df_delivery.apply(yellow, axis=1)
        df_delivery.style.apply(row_style, axis=1)

        df_delivery.loc[df_delivery['yellow']==True, '택배박스 갯수'] = 0
        df_delivery.loc[df_delivery['yellow']==True, '운임Type'] = '-'

        def compact(row):
            result = []
            for i in zip(row['품목'], row['수량']):
                l = ' - '.join(str(e) for e in i) + '개';
                result.append(l)
            return ' / '.join(result)

        df_delivery['품목'] = df_delivery.apply(compact, axis=1)

        def delivery(row):
            result = ''
            msg = [m for m in row['배송메세지'] if m]
            return ' . '.join(msg)

        df_delivery['배송메세지'] = df_delivery.apply(delivery, axis=1)

        return df_delivery, df_order


    def __str__(self):

        return u'{} {}'.format(self.title, self.sender)

    def prepare_reply(self, df_logistics):

        email = self
        for attachment in email.attachments.all():
            df_delivery = pd.read_csv(attachment.order_data_path)

            df = df_delivery[['고객성명', '주문번호']].copy()
            df = df.rename(columns={
                '고객성명': '받는분'
            })

            df = pd.concat([df.set_index('주문번호'), df_logistics.set_index('order_no')], axis=1, join='inner').reset_index()

            df = df[['logis_no', '받는분', 'addr', 'product']]
            df = df.rename(columns={
                'logis_no': '운송장번호',
                'addr': '받는분주소',
                'product': '품목명',
            })

            if df.shape[0] != df_delivery.shape[0]:
                raise ValueError('운송장 번호 못찾음')

            attachment.reply_html = df.to_html()
            attachment.save()

    @property
    def reply_html(self):

        result = []
        for attachment in self.attachments.all():
            result.append(attachment.reply_html)

        return '<br/>'.join(result)



def sort_by_column(df, column_name):

    ord_dict = {}
    ordering_list = []

    for idx, value in enumerate(df[column_name]):
        if value not in ord_dict:
            ord_dict[value] = len(ord_dict)
        ordering_list.append((ord_dict[value], idx))

    df['ord'] = ordering_list
    df.sort_values(by='ord')

    return df


def row_style(row):
    if row['yellow']:
        return pd.Series('background-color: yellow', row.index)

    return pd.Series('', row.index)



def xstr(s):
    res = s or ""
    return "".join(res.split())
