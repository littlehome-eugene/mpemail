# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-07-24 08:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mpemail', '0003_email_msg_mid'),
    ]

    operations = [
        migrations.AddField(
            model_name='email',
            name='data',
            field=models.TextField(default=b''),
        ),
    ]
