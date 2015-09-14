from django.core import serializers
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from main.models import Camper, UnregisteredUser


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


def get_or_send_email(address, trip, first=None):
    try:
        camper = Camper.objects.filter(user__email=address)[0]
        trip.invited.add(camper)
        invite_email(address, name=first, trip=trip)
        return trip
    except:
        unregistered_user = \
            UnregisteredUser.objects.get_or_create(email=address,
                                                   first_name=first)[
                0]
        trip.unregistered_user.add(unregistered_user)
        invite_email(address, name=first, trip=trip)
    return trip


def invite_email(address, name, trip):
    body="Hello {name}, You Have Been invited on a trip at Around The Fire. aroundthefire.herokuapps.com/trip/{trip}".format(name=name, trip=trip.pk),
    send_mail("You've been invited on a trip at Around The Fire", body,
      "Around The Fire <ericturnernv@gmail.com>", [address])
    return
    # or
    # mail = EmailMultiAlternatives(
    #     subject="You've Been invited on a trip at Around The Fire",
    #     body="hello {name}, You Have Been invited on a trip at Around The Fire. Go to aroundthefire.herokuapps.com/trip/{trip} to see what you're missing".format(
    #         name=name, trip=trip.pk),
    #     from_email="Around The Fire <ericturnernv@gmail.com>",
    #     to=[address],
    #     headers={"Reply-To": "support@sendgrid.com"}
    # )
    # mail.attach_alternative("<p>This is a simple HTML email body</p>",
    #                         "text/html")
    # mail.send()
