from django.contrib import admin

# Register your models here.
from main.models import Trip, Location, Camper, Address


@admin.register(Camper)
class CamperAdmin(admin.ModelAdmin):
    list_display = ('user',)

@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ('owner', 'start_date', 'end_date', 'location',)

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Address)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('lat', 'lng', 'weather_place', 'zip')