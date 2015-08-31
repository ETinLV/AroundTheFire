import datetime
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Model


class Camper(models.Model):
    """Model for site user. aka Campers"""
    user = models.OneToOneField(User, null=True)
    zip = models.CharField(max_length=10, null=True)
    friends = models.ManyToManyField('self')

    def __str__(self):
        return '{}'.format(self.user.username)


class Trip(models.Model):
    """Model for trips created by campers"""
    owner = models.OneToOneField(Camper, related_name="owner", null=True)
    attending = models.ManyToManyField(Camper, related_name='attending',
                                       null=True)
    start_date = models.DateField(blank=False, null=True)
    end_date = models.DateField(blank=False, null=True)
    location = models.OneToOneField('Location', related_name='location',
                                    null=True)

    def __str__(self):
        return '{}. {}, {}'.format(self.owner.user.username, self.location, self.start_date)


class Location(models.Model):
    """Model for campsites"""
    name = models.CharField(max_length=200, null=True)
    lat = models.CharField(max_length=30, null=True)
    long = models.CharField(max_length=30, null=True)
    weather_place = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return '{}'.format(self.name)
