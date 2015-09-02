import json

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, render_to_response
from django.utils.decorators import method_decorator
from django.utils.safestring import mark_safe
from django.views.generic import View, CreateView, DetailView
import requests

from main.apikeys import googlekey, trailkey
from main.forms import CamperCreateForm
from main.models import Camper, Trip, Location


class UserHome(View):

    def get(self, request, *arg):
        self.jslocations = serializers.serialize('json', Location.objects.all(),
                                    fields=('lat', 'lng', 'name', 'city', 'zip', 'pk'))
        if self.request.user.pk is not None:
            context = {'camper': self.request.user.camper,
                       'locations': Location.objects.all(),
                       'jslocations': mark_safe(self.jslocations)}
            return render_to_response(template_name='user/home.html',
                                      context=context)
        else:
            context = {'locations': Location.objects.all(),
                       'jslocations': mark_safe(self.jslocations)}
            return render_to_response(template_name='default.html',
                                      context=context)


def create_camper(request):
    """Camper Registration view to register.html"""
    if request.method == 'POST':
        form = CamperCreateForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = form.save()
            camper = Camper()
            make_addres(camper, zip=data['zip'])
            camper.user = user
            camper.save()
            user = authenticate(username=request.POST['username'],
                                password=request.POST['password1'])
            login(request, user)

            return HttpResponseRedirect(reverse('home'))

    else:
        form = CamperCreateForm()

    return render(request, 'user/register.html',
                  {'form': form})


class TripDetail(DetailView):
    model = Trip
    template_name = 'trip/detail.html'


# TODO: Make sure user has permission to see the trip
# TODO: Check if past or upcoming trip

class LocationDetail(DetailView):
    model = Location
    template_name = 'location/detail.html'


class LocationCreate(CreateView):
    model = Location
    fields = ('name',)
    template_name = "location/create.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LocationCreate, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse('home')

    def form_valid(self, form):
        form.instance.owner = self.request.user.camper
        return super(LocationCreate, self).form_valid(form)


# TODO add the adress into the location
class TripCreate(CreateView):
    model = Trip
    fields = ('start_date', 'end_date')
    template_name = "trip/create.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(TripCreate, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse('home')

    def form_valid(self, form):
        form.instance.owner = self.request.user.camper
        return super(TripCreate, self).form_valid(form)


# TODO: when creating trip, can click map to create new site and return to trip

def make_addres(object, zip=None, lat=None, lng=None):
    """
    Takes an object and either a zip code or lat/lng value and creates the other
    data. Also saves the nearest city
    """

    if zip:
        response = requests.get(
            'https://maps.googleapis.com/maps/api/geocode/json?address={zip}&components=country:US&key={googlekey}'.format(
                zip=zip, googlekey=googlekey))
        data = json.loads(response.content.decode('utf-8'))
        data = data['results'][0]
        object.zip = zip
        object.lat = data['geometry']['location']['lat']
        object.lng = data['geometry']['location']['lng']
        object.city = data['address_components'][1]['short_name']
        object.save()
        return object
    else:
        response = requests.get(
            'https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lng}&key={googlekey}'.format(
                lat=lat, lng=lng, googlekey=googlekey))
        data = json.loads(response.content.decode('utf-8'))
        data = data['results'][0]
        object.city = data['address_components'][1]['short_name']
        try:
            object.zip = data['address_components'][5]['short_name']
        except:
            object.zip = None
        object.save()
        return object


def call_trail_api(lat='0', lng='0', radius=180, limit=100):
    response = requests.get(
        "https://trailapi-trailapi.p.mashape.com/?lat={lat}&limit={limit}&lon={lng}&q[activities_activity_type_name_eq]=camping&q[country_cont]=united+states&radius={radius}".format(
            lat=lat, limit=limit, lng=lng, radius=radius),
        headers={
            "X-Mashape-Key": trailkey,
            "Accept": "text/plain"
        })
    data = json.loads(response.content.decode('utf-8'))
    return data


def api_create_locations(lat, lng):
    for object in call_trail_api(lat=lat, lng=lng)[
        'places']:
        location = Location.objects.create(lat=object['lat'], lng=object['lon'])
        make_addres(location, lat=location.lat, lng=location.lng)
        location.name = object['name']
        location.save()

#
#     response = requests.get(
#     "http://api.wunderground.com/api/{}/conditions/forecast/q/CA/{}.json".format(weatherkey,
#         location))
#     data = json.loads(response.content.decode('utf-8'))
#     return (data, data2)
#
#
# """quick test to make sure the api call is working. it is."""
# class MyView(View):
#     def get(self, request):
#         results = call_api('las vegas')
#         return HttpResponse(results)
