# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_auto_20150913_1048'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2015, 9, 13, 10, 51, 37, 864051)),
        ),
        migrations.AlterField(
            model_name='photo',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2015, 9, 13, 10, 51, 37, 863015)),
        ),
        migrations.AlterField(
            model_name='review',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2015, 9, 13, 10, 51, 37, 865362)),
        ),
        migrations.AlterField(
            model_name='trip',
            name='unregistered_user',
            field=models.ManyToManyField(related_name='invited', to='main.UnregisteredUser'),
        ),
    ]
