from django.contrib import admin
from main.models import Trip, Location, Camper, Photo, Review, Message, \
    UnregisteredUser


# Create Admin display for all models

@admin.register(Camper)
class CamperAdmin(admin.ModelAdmin):
    list_display = ('user', 'zip',)


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ('owner', 'start_date', 'end_date', 'location',)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'lat', 'lng', 'zip', 'pk')


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('url', 'location', 'trip')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('location', 'owner')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('trip', 'owner')


@admin.register(UnregisteredUser)
class UnregisteredUserAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'email')
