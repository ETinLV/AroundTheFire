import datetime
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


class Trip(models.Model):
    """Model for trips created by campers"""
    owner = models.OneToOneField(Camper, related_name="owner", null=True)
    attending = models.ManyToManyField(Camper, related_name='attending',)
    start_date = models.DateField(blank=False, null=True)
    end_date = models.DateField(blank=False, null=True)
    location = models.OneToOneField('Location', related_name='location',
                                    null=True)

    def __str__(self):
        return '{}. {}, {}'.format(self.owner.user.username, self.location, self.start_date)


class Location(models.Model):
    """Model for campsites"""
    name = models.CharField(max_length=200, null=True)
    zip = models.CharField(max_length=10, null=True, blank=True)
    lat = models.CharField(max_length=30, null=True)
    lng = models.CharField(max_length=30, null=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    def __str__(self):
        return '{}'.format(self.name)
