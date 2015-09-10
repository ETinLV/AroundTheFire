from django.core import serializers


def marker_set(request):
        invited = set()
        upcoming = set()
        past = set()
        for trip in request.user.camper.invited_trips:
            invited.add(trip.location)
        for trip in request.user.camper.upcoming_trips:
            if trip.location in invited:
                pass
            else:
                upcoming.add(trip.location)
        for trip in request.user.camper.past_trips:
            if trip.location in invited or trip.location in upcoming:
                pass
            else:
                past.add(trip.location)
        invited = serializers.serialize('json', invited,
                                                 fields=(
                                                 'lat', 'lng', 'name', 'city',
                                                 'zip', 'pk',))
        upcoming = serializers.serialize('json', upcoming,
                                                 fields=(
                                                 'lat', 'lng', 'name', 'city',
                                                 'zip', 'pk',))
        past = serializers.serialize('json', past,
                                                 fields=(
                                                 'lat', 'lng', 'name', 'city',
                                                 'zip', 'pk',))
        return (invited, upcoming, past)