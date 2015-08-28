import datetime
from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from django.db.models import Model


class Camper(models.Model):
    user = models.OneToOneField(User)
    zip = models.CharField(max_length=10)
    friends = models.ManyToManyField('self', blank=True, null=True)

class Trip(models.Model):
    owner = models.OneToOneField(Camper)
    attending = models.ManyToManyField(Camper, null=True, blank=True, related_name='attending')
    date = models.DateField(default=datetime.datetime.now())