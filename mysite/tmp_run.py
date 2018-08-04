import sys
import os
from django.utils import timezone
import datetime
from django.db.models import Count
import django
import pandas as pd

ROOT_DIR = os.path.dirname(__file__)  # current dir

sys.path.append(ROOT_DIR)
sys.path.append(os.path.join(ROOT_DIR, '..'))
sys.path.append(os.path.join(ROOT_DIR, 'apps'))

# sys.path.append('/home/eugenekim/outsource/mail/')
# sys.path.append('/home/eugenekim/outsource/mail/mysite/')
# sys.path.append('/home/eugenekim/outsource/mail/mysite/apps/')


os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'mysite.settings')
django.setup()

from django.conf import settings

from mpemail.models.email import Email
from pandas import ExcelWriter


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



emails = Email.objects.eligible_for_order()

df_delivery = pd.DataFrame(columns=columns_delivery)
df_order = pd.DataFrame(columns=columns_order)
for email in emails:
    result = email.process_order()
    if result:
        df_delivery_1, df_order_1 = result
    else:
        continue

    df_delivery = pd.concat([df_delivery, df_delivery_1], axis=0)
    df_order = pd.concat([df_order, df_order_1], axis=0)


writer = ExcelWriter(os.path.join(settings.OUTPUT_DIR, 'logistics.xlsx'))

import pdb; pdb.set_trace()
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
