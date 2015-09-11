# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_auto_20150911_1351'),
    ]

    operations = [
        migrations.AlterField(
            model_name='camper',
            name='friends',
            field=models.ManyToManyField(related_name='friends_rel_+', blank=True, to='main.Camper'),
        ),
        migrations.AlterField(
            model_name='message',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2015, 9, 11, 14, 0, 44, 501449)),
        ),
        migrations.AlterField(
            model_name='review',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2015, 9, 11, 14, 0, 44, 502367)),
        ),
    ]
