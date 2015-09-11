# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import datetime


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('content', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(default=datetime.datetime(2015, 9, 11, 13, 51, 53, 159397))),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('url', models.URLField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('content', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(default=datetime.datetime(2015, 9, 11, 13, 51, 53, 160126))),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddField(
            model_name='camper',
            name='city',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='camper',
            name='friends',
            field=models.ManyToManyField(to='main.Camper', related_name='friends_rel_+'),
        ),
        migrations.AddField(
            model_name='camper',
            name='lat',
            field=models.FloatField(max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='camper',
            name='lng',
            field=models.FloatField(max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='camper',
            name='user',
            field=models.OneToOneField(to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='camper',
            name='zip',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='location',
            name='api_id',
            field=models.CharField(max_length=100, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='location',
            name='city',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='location',
            name='lat',
            field=models.FloatField(max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='location',
            name='lng',
            field=models.FloatField(max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='location',
            name='name',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='location',
            name='zip',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='trip',
            name='attending',
            field=models.ManyToManyField(to='main.Camper', blank=True, related_name='attending'),
        ),
        migrations.AddField(
            model_name='trip',
            name='declined',
            field=models.ManyToManyField(to='main.Camper', blank=True, related_name='declined'),
        ),
        migrations.AddField(
            model_name='trip',
            name='description',
            field=models.TextField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='trip',
            name='end_date',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='trip',
            name='invited',
            field=models.ManyToManyField(to='main.Camper', blank=True, related_name='invited'),
        ),
        migrations.AddField(
            model_name='trip',
            name='location',
            field=models.ForeignKey(to='main.Location', null=True, related_name='location'),
        ),
        migrations.AddField(
            model_name='trip',
            name='max_capacity',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='trip',
            name='owner',
            field=models.ForeignKey(to='main.Camper', null=True, related_name='created'),
        ),
        migrations.AddField(
            model_name='trip',
            name='start_date',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='trip',
            name='title',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='review',
            name='location',
            field=models.ForeignKey(to='main.Location', blank=True, null=True, related_name='reviews'),
        ),
        migrations.AddField(
            model_name='review',
            name='owner',
            field=models.ForeignKey(to='main.Camper', blank=True, null=True, related_name='reviews'),
        ),
        migrations.AddField(
            model_name='photo',
            name='location',
            field=models.ForeignKey(to='main.Location', blank=True, null=True, related_name='photos'),
        ),
        migrations.AddField(
            model_name='photo',
            name='trip',
            field=models.ForeignKey(to='main.Trip', blank=True, null=True, related_name='photos'),
        ),
        migrations.AddField(
            model_name='message',
            name='owner',
            field=models.ForeignKey(to='main.Camper', blank=True, null=True, related_name='messages'),
        ),
        migrations.AddField(
            model_name='message',
            name='trip',
            field=models.ForeignKey(to='main.Trip', blank=True, null=True, related_name='messages'),
        ),
    ]
