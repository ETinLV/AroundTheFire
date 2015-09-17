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
        'invited': location_list_serializer(invited),
        'upcoming': location_list_serializer(upcoming),
        'past': location_list_serializer(past),
    }
    return locations


def location_list_serializer(location_list):
    """JSON serialize a list of locations"""
    if location_list is not None:
        data = serializers.serialize('json', location_list,
                                     fields=(
                                         'lat', 'lng', 'name', 'city',
                                         'zip', 'pk',))
        return data
    else:
        return None

def get_or_send_email(address, trip, first=None):
    """Find a user object or create an unregistered user and send an email"""

    try:
        camper = Camper.objects.filter(user__email=address)[0]
        trip.invited.add(camper)
        invite_email(address, name=first, trip=trip)
        return trip
    except IndexError:
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


def convert_unregistered_user(data, camper):
    """ Check if new user was previously an unregistered user"""
    try:
        # If the user was unregistered, add the registered user
        # to the invited list of the trips they were previously invited on
        unregistered_user = UnregisteredUser.objects.get(
            email=data['email'])
        for trip in unregistered_user.invited.all():
            trip.invited.add(camper)
            trip.save()
        unregistered_user.delete()
    except UnregisteredUser.DoesNotExist:
        pass
