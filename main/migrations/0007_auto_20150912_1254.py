# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_auto_20150912_1253'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='photo',
            options={'ordering': ['-created_at']},
        ),
        migrations.AlterField(
            model_name='message',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2015, 9, 12, 12, 54, 23, 332396)),
        ),
        migrations.AlterField(
            model_name='photo',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2015, 9, 12, 12, 54, 23, 331568)),
        ),
        migrations.AlterField(
            model_name='review',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2015, 9, 12, 12, 54, 23, 333198)),
        ),
    ]
