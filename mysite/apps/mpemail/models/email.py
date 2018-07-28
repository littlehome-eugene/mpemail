# -*- coding: utf-8 -*-
import os
import re
from django.db import models
import urlparse
from django.conf import settings
from django.db.models.query import QuerySet
import pandas as pd


product_excel = os.path.join(settings.PROJECT_DIR, 'apps/mpemail/config/product.xlsx')
df_product = pd.read_excel(product_excel)

keyword_title_excel = os.path.join(settings.PROJECT_DIR, 'apps/mpemail/config/keyword-title.xlsx')
df_keyword = pd.read_excel(keyword_title_excel)



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
        'application/vnd.ms-excel'
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

        url = urlparse.urljoin(settings.MAILPILE_URL, url)

        return url

    def process_order(self):

        email = self
        process_order_fail_reason = None

        attachment = email.attachment

        df = pd.read_excel(attachment)


        product = df_keyword['품목'.decode('utf-8')]
        count = df_keyword['수량'.decode('utf-8')]

        product_column = None
        count_column = None


        order_list = []
        for column in df.columns:
            if column in product.tolist():
                product_column = column
            if column in count.tolist():
                count_column = column

        try:
            if product_column is None:
                error = '품목 없음'
                raise ValueError
            if count_column is None:
                error = '수량 없음'
                raise ValueError

            for index, row in df.iterrows():
                products = row[product_column].split('//')
                count = row[count_column]
                count_sum = 0

                order_dict = {
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
                        count = productcode_count_pairs[0][1] or 1
                        count_sum += count
                    else:
                        error = '품목코드 파싱 실패'
                        raise ValueError

                    order_dict.setdefault('품목코드', [])
                    order_dict['품목코드'].append(product_code)
                    order_dict['수량'] = count

                    product = df_product.loc[df_product['품목코드'.decode('utf-8')]==product_code]
                    product_name = product.iloc[0]['품목명'.decode('utf-8')]
                    order_dict.setdefault('품목명', [])
                    order_dict['품목명'].append(product_name)
                    order_list.append(order_dict)

        except ValueError:
            print error
            pass


        df_result = pd.DataFrame(order_list)


        import pdb; pdb.set_trace()
        pass