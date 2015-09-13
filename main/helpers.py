from django.core import serializers
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives

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



def send_mail(request):
    send_mail("You've been invited on a trip", "This is a test of email",
      "Around The Fire <ericturnernv@gmail.com>", ["ericturnernv@gmail.com"])
    success = True
    return success

# # or
# mail = EmailMultiAlternatives(
#   subject="Your Subject",
#   body="This is a simple text email body.",
#   from_email="Yamil Asusta <hello@yamilasusta.com>",
#   to=["yamil@sendgrid.com"],
#   headers={"Reply-To": "support@sendgrid.com"}
# )
# mail.attach_alternative("<p>This is a simple HTML email body</p>", "text/html")
#
#     mail.send()