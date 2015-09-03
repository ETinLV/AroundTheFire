from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, render_to_response
from django.utils.decorators import method_decorator
from django.utils.safestring import mark_safe
from django.views.generic import View, CreateView, DetailView

from main.apicalls import make_address
from main.forms import CamperCreateForm
from main.models import Camper, Trip, Location


class Home(View):
    """Homepage View. Different templates depending if user is logged in or not"""

    def get(self, request, *arg):
        # serialize the campsites
        self.jslocations = serializers.serialize('json', Location.objects.all(),
                                                 fields=(
                                                     'lat', 'lng', 'name',
                                                     'city',
                                                     'zip', 'pk'))
        # if user is lgged in, sent to homepage
        if self.request.user.pk is not None:
            context = {'camper': self.request.user.camper,
                       'locations': Location.objects.all(),
                       'jslocations': mark_safe(self.jslocations)}
            return render_to_response(template_name='user/home.html',
                                      context=context)
        # if not logged in, send to default page
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
            # Send to function to add zip and city
            make_address(camper, zip=data['zip'])
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


class LocationDetail(DetailView):
    """Detail view for a location"""
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
        make_address(object=form.instance, lat=form.data['lat'], lng=form.data['lng'])
        return super(LocationCreate, self).form_valid(form)


class TripDetail(DetailView):
    model = Trip
    template_name = 'trip/detail.html'


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
        """Make the owner of the trip the user who created it"""
        form.instance.owner = self.request.user.camper
        return super(TripCreate, self).form_valid(form)


# TODO: when creating trip, can click map to create new site and return to trip


