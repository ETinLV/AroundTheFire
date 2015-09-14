# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0011_auto_20150913_2207'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='api_id',
            field=models.CharField(unique=True, null=True, blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='message',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2015, 9, 13, 22, 8, 11, 310791)),
        ),
        migrations.AlterField(
            model_name='photo',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2015, 9, 13, 22, 8, 11, 309192)),
        ),
        migrations.AlterField(
            model_name='review',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2015, 9, 13, 22, 8, 11, 312686)),
        ),
    ]
