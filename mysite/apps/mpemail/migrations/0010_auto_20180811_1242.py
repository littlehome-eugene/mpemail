# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-08-11 12:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mpemail', '0009_auto_20180811_0932'),
    ]

    operations = [
        migrations.AddField(
            model_name='email',
            name='order_data_path',
            field=models.CharField(blank=True, default='', max_length=256),
        ),
        migrations.AddField(
            model_name='email',
            name='reply_html',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='email',
            name='sender_name',
            field=models.CharField(blank=True, default='', max_length=128),
        ),
        migrations.AddField(
            model_name='email',
            name='timestamp',
            field=models.IntegerField(db_index=True, default=0),
        ),
    ]