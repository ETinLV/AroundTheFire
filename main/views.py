from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
import json
from django.shortcuts import render, render_to_response

# Create your views here.
from django.utils.decorators import method_decorator
from django.utils.safestring import mark_safe
from django.views.generic import View, CreateView, DetailView, ListView
import requests
from main.apikeys import trailkey, weatherkey
from main.forms import CamperCreateForm
from main.models import Camper, Trip, Location


class Default(View):
    def get(self, request, *args, **kwargs):
        if request.user:
            context = {'locations': Location.objects.all()}
            return render_to_response(template_name='user/home.html', context=context)
        else:
           return HttpResponseRedirect(reverse('default'))

class UserHome(View):
    jslocations = serializers.serialize('json', Location.objects.all(), fields=('lat','long'))
    def get(self, request, *args, **kwargs):
        if self.request.user.pk is not None:
            context = {'camper': self.request.user.camper, 'locations': Location.objects.all(), 'jslocations': mark_safe(self.jslocations)}
            return render_to_response(template_name='user/home.html', context=context)
        else:
            context = {'locations': Location.objects.all(), 'jslocations': mark_safe(self.jslocations)}
            return render_to_response(template_name='default.html', context=context)

def create_camper(request):
    """Camper Registration view to register.html"""
    if request.method == 'POST':
        form = CamperCreateForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = form.save()
            camper = Camper()
            camper.user = user
            camper.zip = data['zip']
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

#TODO: Make sure user has permission to see the trip
#TODO: Check if past or upcoming trip

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

class TripCreate(CreateView):
    model = Trip
    fields = ('start_date', 'end_date' )
    template_name = "trip/create.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(TripCreate, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse('home')

    def form_valid(self, form):
        form.instance.owner = self.request.user.camper
        return super(TripCreate, self).form_valid(form)
#TODO: when creating trip, can click map to create new site and return to trip



# def call_api(location):
#     response = requests.get(
#         "https://trailapi-trailapi.p.mashape.com/?q[activities_activity_type_name_eq]=camping&q[city_cont]={}".format(
#             location),
#         headers={
#             "X-Mashape-Key": trailkey,
#             "Accept": "text/plain"
#                 })
#     data2 = json.loads(response.content.decode('utf-8'))
#
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



