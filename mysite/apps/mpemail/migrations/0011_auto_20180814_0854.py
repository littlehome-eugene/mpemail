# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-08-14 08:54
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mpemail', '0010_auto_20180811_1242'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='email',
            name='attachment',
        ),
        migrations.RemoveField(
            model_name='email',
            name='attachment_count',
        ),
        migrations.RemoveField(
            model_name='email',
            name='order_data_path',
        ),
        migrations.RemoveField(
            model_name='email',
            name='reply_html',
        ),
    ]
