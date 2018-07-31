# -*- coding: utf-8 -*-
import os
import re
from django.db import models

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
df_company = pd.read_excel(company_excel)


class EmailQuerySet(QuerySet):

    def eligible_for_order(self):

        queryset = self

        queryset = queryset.filter(
            eligible_for_process=True
        ).filter(
            auto_order_status__in=['initial', 'process_fail']
        )
        return queryset


class EmailManager(models.Manager):

    pass


class Email(models.Model):

    ALLOWED_EXCEL_MIME_TYPES = [
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    ]

    AUTO_STATUS = [
        ['initial', 'initial'],
        ['process_success', 'process_success'],
        ['process_fail', 'process_fail'],
        ['done', 'done'],
    ]

    MANUAL_STATUS = [
        ['initial', 'initial'],
        ['done', 'done'],
    ]

    # email data
    msg_mid = models.CharField(max_length=128, blank=True, db_index=True)
    msg_id = models.CharField(max_length=128, blank=True, db_index=True)
    title = models.CharField(max_length=2048, blank=True, db_index=True)
    sender = models.CharField(max_length=128, blank=True, db_index=True)

    excel_attachment_count = models.IntegerField(default=0)
    body_text = models.TextField(default='')
    attachment = models.FileField(upload_to='attachment/%Y/%m/%d/', null=True)
    attachment_count = models.IntegerField(default=0)  # this is used in part-{attachment_count}
    # email data

    eligible_for_process = models.BooleanField(default=False, db_index=True)

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

    objects = EmailManager.from_queryset(EmailQuerySet)()


    def check_eligible_for_process(self):

        email = self

        if email.excel_attachment_count != 1:
            return False

        return True

    def attachment_download_url(self):

        email = self

        url = '/message/download/get/={mid}/part-{count}/'.format(
            mid=email.msg_mid,
            count=email.attachment_count
        )

        url = urljoin(settings.MAILPILE_URL, url)

        return url

    def process_order(self):

        error = None
        email = self
        process_order_fail_reason = None

        attachment = email.attachment

        df = pd.read_excel(attachment, dtype=str)

        df_seller = df_company.loc[df_company['email'] == email.sender]
        try:
            if df_seller.empty:
                error = '판매자 못찾음'
                raise ValueError
            seller_dict = df_seller.iloc[0].to_dict()
        except ValueError:
            print(error)
            return

        product = df_keyword['품목']
        count = df_keyword['수량']

        product_column = None
        count_column = None

        customer = df_keyword['고객성명']
        postal = df_keyword['우편번호']
        address = df_keyword['주소']
        phone = df_keyword['전화번호']
        message = df_keyword['배송메시지']

        customer_column = None
        postal_column = None
        address_column = None
        phone_column = None
        message_column = None

        sender = df_keyword['보내는이']
        sender_phone = df_keyword['보내는이 전화번호']
        sender_cellphone = df_keyword['보내는이 핸드폰']

        sender_column = None
        sender_phone_column = None
        sender_cellphone_column = None

        order_list = []
        for column in df.columns:
            if column in product.tolist():
                product_column = column
            elif column in count.tolist():
                count_column = column
            elif column in customer.tolist():
                customer_column = column
            elif column in postal.tolist():
                postal_column = column
            elif column in address.tolist():
                address_column = column
            elif column in phone.tolist():
                phone_column = column
            elif column in message.tolist():
                message_column = column
            elif column in sender.tolist():
                sender_column = column
            elif column in sender_phone.tolist():
                sender_phone_column = column
            elif column in sender_cellphone.tolist():
                sender_cellphone_column = column

        try:
            if product_column is None:
                error = '품목 없음'
                raise ValueError
            if count_column is None:
                error = '수량 없음'
                raise ValueError
            if customer_column is None:
                error = '고객성명 없음'
                raise ValueError
            if postal_column is None:
                error = '우편번호 없음'
                raise ValueError
            if address_column is None:
                error = '주소 없음'
                raise ValueError
            if phone_column is None:
                error = '전화번호 없음'
                raise ValueError
            if message_column is None:
                error = '배송메시지 없음'
                raise ValueError

            for index, row in df.iterrows():
                products = row[product_column].split('//')
                count_by_countcolumn = int(row[count_column])
                count_sum = 0

                if sender_column:
                    sender = row[sender_column]
                else:
                    sender = seller_dict['거래처명']

                if sender_phone_column:
                    sender_phone = row[sender_phone_column]
                else:
                    sender_phone = seller_dict['전화']

                if sender_cellphone_column:
                    sender_cellphone = row[sender_cellphone_column]
                else:
                    sender_cellphone = seller_dict['핸드폰']


                order_dict = {
                    '고객성명': row[customer_column],
                    '우편번호': row[postal_column],
                    '주소': row[address_column].strip(),
                    '전화번호': str(row[phone_column] or ""),
                    '배송메시지': row[message_column],
                    '핸드폰번호': '',  # todo

                    '보내는분 성명': sender,
                    '보내는분 전화': str(sender_phone or ""),
                    '보내는분 핸드폰': str(sender_cellphone or ""),
                    '보내는분 우편본호': seller_dict['우편번호'],
                    '보내는분 주소': seller_dict['주소'],

                    '택배박스 갯수': '',
                    '운임Type': '',
                    '주문번호': str(uuid.uuid4()),

                }
                for product in products:
                    productcode_count_pairs_bogus = re.findall('[^[]+\[([^]]+)\][^\d[]*(?:(\d)\s*[^개\d]+)?', row[product_column])
                    if productcode_count_pairs_bogus:
                        if productcode_count_pairs_bogus[0][1]:
                            error = '수량 파싱 실패'
                            raise ValueError

                    productcode_count_pairs = re.findall('[^[]+\[([^]]+)\][^\d[]*(?:(\d)\s*개)?', row[product_column])
                    if len(productcode_count_pairs) == 1:

                        product_code = productcode_count_pairs[0][0]
                        count = int(productcode_count_pairs[0][1]) or 1
                        count_sum += count
                    else:
                        error = '품목코드 파싱 실패'
                        raise ValueError

                    order_dict.setdefault('품목코드', [])
                    order_dict['품목코드'].append(product_code)
                    order_dict['품목코드_flat'] = product_code

                    product = df_product.loc[df_product['품목코드']==product_code]
                    product_name = product.iloc[0]['품목명']
                    order_dict.setdefault('품목', [])
                    order_dict['품목'].append(product_name)
                    order_dict['품목_flat'] = product_name

                    order_dict.setdefault('수량', [])
                    order_dict['수량'].append(count)
                    order_dict['수량_flat'] = count

                    order_list.append(order_dict)


                if count_by_countcolumn and count_by_countcolumn != count_sum:
                    # 수량 column 과 sum 이 다름
                    order_list.pop()
                    raise ValueError

        except ValueError:
            print(error)
            return

        # place same address rows together

        df_delivery = pd.DataFrame(order_list)

        df_order = df_delivery[['수량_flat', '품목코드_flat']].copy()

        df_order = df_order.rename(columns={
            '수량_flat':'수량',
            '품목코드_flat':'품목코드',
        })

        df_order.groupby('품목코드').agg({'수량':'sum'})

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
        df_order['규격'] = product.iloc[0]['규격']
        df_order['단가(vat포함)'] = ''  # todo
        df_order['외화금액'] = ''
        df_order['공급가액'] = ''  # todo
        df_order['부가세'] = ''  # todo

        df_order['적요'] = attachment.name.split('/')[-1]
        df_order['부대비용'] = ''
        df_order['생상전표생성'] = ''
        df_order['Ecount'] = 'Ecount'


        df_delivery = sort_by_column(df_delivery, '주소')

        address_prev = None
        index_prev = None
        df_delivery['to_be_deleted'] = False
        for index, row in df_delivery.iterrows():
            if address_prev and row['주소'] == address_prev:
                df_delivery.loc[index_prev, '품목'].extend(
                     df_delivery.loc[index, '품목']
                )
                df_delivery.loc[index_prev, '수량'].extend(
                     df_delivery.loc[index, '수량']
                )
                df_delivery.loc[index, 'to_be_deleted'] = True
            else:
                address_prev = row['주소']
                index_prev = index

        df_delivery = df_delivery[df_delivery['to_be_deleted'] != True]

        df_delivery = sort_by_column(df_delivery, '고객성명')
        df_delivery = sort_by_column(df_delivery, '전화번호')
        df_delivery = sort_by_column(df_delivery, '핸드폰번호')

        index_prev = None
        df_delivery['maybe_same_customer'] = False
        for index, row in df_delivery.iterrows():
            if index_prev:
                customer_prev = df_delivery.loc[index_prev, '고객성명']
                phone_prev = df_delivery.loc[index_prev, '전화번호']
                cellphone_prev = df_delivery.loc[index_prev, '핸드폰번호']
                if (row['고객성명'] == customer_prev or
                    row['전화번호'] == phone_prev or
                    row['핸드폰번호'] == cellphone_prev):

                    df_delivery.loc[index, 'maybe_same_customer'] = True
                    df_delivery.loc[index_prev, 'maybe_same_customer'] = True
                    # yellow
                    pass
            else:
                index_prev = index

        df_delivery.loc[df_delivery['maybe_same_customer']==True, '택배박스 갯수'] = 0
        df_delivery.loc[df_delivery['maybe_same_customer']==True, '운임Type'] = '-'
        df_delivery.style.apply(row_style, axis=1)


        return df_delivery, df_order


    def __str__(self):

        return u'{} {}'.format(self.title, self.sender)


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
    if row.maybe_same_customer:
        return pd.Series('background-color: yellow', row.index)
    else:
        return pd.Series('', row.index)
