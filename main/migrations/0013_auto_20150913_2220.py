# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_auto_20150913_2208'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='camper',
            name='friends',
        ),
        migrations.AlterField(
            model_name='message',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2015, 9, 13, 22, 20, 30, 210798)),
        ),
        migrations.AlterField(
            model_name='photo',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2015, 9, 13, 22, 20, 30, 210055)),
        ),
        migrations.AlterField(
            model_name='review',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2015, 9, 13, 22, 20, 30, 211662)),
        ),
        migrations.AlterField(
            model_name='trip',
            name='unregistered_user',
            field=models.ManyToManyField(related_name='invited', blank=True, to='main.UnregisteredUser'),
        ),
    ]
