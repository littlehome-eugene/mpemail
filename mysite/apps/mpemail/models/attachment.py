from django.db import models
from django.conf import settings
from urllib.parse import urlparse, urlunparse, urljoin, parse_qsl, ParseResult, unquote


class Attachment(models.Model):

    email = models.ForeignKey('mpemail.Email', related_name='attachments')

    attachment = models.FileField(upload_to='attachment/%Y/%m/%d/', null=True)
    attachment_count = models.IntegerField(default=0, db_index=True)  # this is used in part-{attachment_count}
    order_data_path = models.CharField(max_length=256, default="", blank=True)
    reply_html = models.TextField(default='')


    def download_url(self):

        email = self.email

        url = '/message/download/get/={mid}/part-{count}/'.format(
            mid=email.msg_mid,
            count=self.attachment_count
        )

        url = urljoin(settings.MAILPILE_URL, url)

        return url
