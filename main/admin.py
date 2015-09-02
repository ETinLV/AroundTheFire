from django.contrib import admin

# Register your models here.
from main.models import Trip, Location, Camper


@admin.register(Camper)
class CamperAdmin(admin.ModelAdmin):
    list_display = ('user', 'zip')

@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ('owner', 'start_date', 'end_date', 'location',)

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'lat', 'lng', 'zip','pk')