import datetime
from itertools import chain
from operator import attrgetter
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Model

"""Repeating fields in "Camper" and "Location" are due to Django having
difficulty serializing data in  OneToOne key objects, so that attempting to pass
a location lat and long in the JS on the template would not work."""


class Camper(models.Model):
    """Model for site user. aka Campers"""
    user = models.OneToOneField(User, null=True)
    friends = models.ManyToManyField('self')
    zip = models.CharField(max_length=10, null=True, blank=True)
    lat = models.CharField(max_length=30, null=True)
    lng = models.CharField(max_length=30, null=True)
    city = models.CharField(max_length=100, null=True, blank=True)


    def __str__(self):
        return '{}'.format(self.user.username)

    @property
    def past_trips(self):
        return set(sorted(
        chain(self.created.filter(end_date__lte=datetime.datetime.now()), self.attending.filter(end_date__lte=datetime.datetime.now())),
        key=attrgetter('end_date')))

    @property
    def upcoming_trips(self):
        return set(sorted(
        chain(self.created.filter(end_date__gt=datetime.datetime.now()), self.attending.filter(end_date__gt=datetime.datetime.now())),
        key=attrgetter('end_date')))

    @property
    def invited_trips(self):
        pass


class Trip(models.Model):
    """Model for trips created by campers"""
    owner = models.ForeignKey(Camper, related_name="created", null=True)
    invited = models.ManyToManyField(Camper, related_name='invited', blank=True)
    attending = models.ManyToManyField(Camper, related_name='attending', blank=True)
    declined = models.ManyToManyField(Camper, related_name='declined', blank=True)
    start_date = models.DateField(blank=False, null=True)
    end_date = models.DateField(blank=False, null=True)
    location = models.ForeignKey('Location', related_name='location',
                                 null=True)
    title = models.CharField(max_length=50, null=True)
    description = models.TextField(max_length=500, null=True, blank=True)
    max_capacity = models.IntegerField(null=True)
    def __str__(self):
        return '{}. {}, {}'.format(self.owner.user.username, self.location,
                                   self.start_date)


class Location(models.Model):
    """Model for campsites"""
    name = models.CharField(max_length=200, null=True)
    zip = models.CharField(max_length=10, null=True, blank=True)
    lat = models.CharField(max_length=30, null=True)
    lng = models.CharField(max_length=30, null=True)
    city = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return '{}'.format(self.name)

class Message(models.Model):
    owner = models.ForeignKey(Camper, null=True, blank=True)
    trip = models.ForeignKey(Trip, null=True, blank=True)
    content = models.TextField(null=True, blank=True)