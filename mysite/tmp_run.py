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


emails = Email.objects.eligible_for_order()

for email in emails:
    email.process_order()
