from django.core import serializers
from django.core.mail import send_mail
from main.models import Camper, UnregisteredUser


def trip_marker_set(request):
    """
    Make a dict of trip locations based on status

    Add each location once based up the hierarchy of its status. Return a
    dictionary with status as key and set of locations as values
    """
    # Create invited set
    invited = set(trip.location for trip in request.user.camper.invited_trips)

    # Create upcoming set, ignoring locations in the invited set
    upcoming = set(
        trip.location for trip in request.user.camper.upcoming_trips if
        trip.location not in invited)

    # Create past set, ignoring locations in the invited and upcoming set
    past = set(trip.location for trip in request.user.camper.past_trips if
               trip.location not in invited and trip.location not in upcoming)
    locations = {
        'invited': location_list_seralizer(invited),
        'upcoming': location_list_seralizer(upcoming),
        'past': location_list_seralizer(past),
    }
    return locations


def location_list_seralizer(location_list):
    """JSON seralize a list of locations"""

    data = serializers.serialize('json', location_list,
                                 fields=(
                                     'lat', 'lng', 'name', 'city',
                                     'zip', 'pk',))
    return data


def get_or_send_email(address, trip, first=None):
    """
    Find a user object or create an unregistered user and send an email
    """

    try:
        camper = Camper.objects.filter(user__email=address)[0]
        trip.invited.add(camper)
        invite_email(address, name=first, trip=trip)
        return trip
    except Camper.DoesNotExist:
        unregistered_user, created = UnregisteredUser.objects.get_or_create(
            email=address,
            first_name=first)
        trip.unregistered_user.add(unregistered_user)
        invite_email(address, name=first, trip=trip)
    return trip


def invite_email(address, name, trip):
    """SendGrid Email Function"""

    subject = "You've been invited on a trip at Around The Fire"
    body = "Hello {name}, You Have Been invited on a trip at Around The Fire " \
           "by {owner}. aroundthefire.herokuapps.com/trip/{trip}".format(
        name=name, owner=trip.owner, trip=trip.pk),
    from_address = "Around The Fire <ericturnernv@gmail.com>"
    send_mail(subject, body,
              from_address, [address])
    return
