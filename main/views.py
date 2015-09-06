import datetime
from django.middleware import csrf
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, render_to_response
from django.template import RequestContext
from django.utils.decorators import method_decorator
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import ensure_csrf_cookie, requires_csrf_token, \
    csrf_protect
from django.views.generic import View, CreateView, DetailView, UpdateView
from main.apicalls import make_address
from main.forms import CamperCreateForm
from main.models import Camper, Trip, Location


class Home(View):
    """Homepage View. Different templates depending if user is logged in or not"""


    def get(self, request, *arg):
        # serialize the campsites
        self.jslocations = serializers.serialize('json', Location.objects.all(),
                        fields=('lat', 'lng', 'name', 'city', 'zip', 'pk'))
        # if user is logged in, send to homepage
        if self.request.user.pk is not None:
            context = {'camper': self.request.user.camper,
                       'locations': Location.objects.all(),
                       'jslocations': mark_safe(self.jslocations),
                       }
            return render_to_response(template_name='user/home.html',
                                      context=context,
                                      context_instance=RequestContext(request))
        # if not logged in, send to default page
        else:
            context = {'locations': Location.objects.all(),
                       'jslocations': mark_safe(self.jslocations)}
            return render_to_response(template_name='default.html',
                                      context=context,
                                      context_instance=RequestContext(request))


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
#TODO make this class based

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

    def get_context_data(self, **kwargs):
        """
        Add extra content to determine if the trip is over or not
        :param kwargs:
        :return:
        """
        """
        :param kwargs:
        :return:
        """
        context = super(TripDetail, self).get_context_data(**kwargs)
        if datetime.datetime.now().year <= self.object.end_date.year and \
            datetime.datetime.now().month <= self.object.end_date.month and \
                datetime.datetime.now().day <= self.object.end_date.day:
                    context['upcoming'] = True
        else:
            context['upcoming'] = False
        #TODO There HAS to be a better way than this....
        return context


class TripCreate(CreateView):
    model = Trip
    fields = ('start_date', 'end_date', 'title', 'description', 'max_capacity', 'invited')
    template_name = "trip/create.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(TripCreate, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(TripCreate, self).get_context_data(**kwargs)
        context['location'] =Location.objects.get(pk=self.kwargs['pk'])
        return context

    def get_success_url(self):
        return reverse('home')

    def form_valid(self, form):
        """Make the owner of the trip the user who created it"""
        form.instance.owner = self.request.user.camper
        form.instance.location = Location.objects.get(pk=self.kwargs['pk'])
        return super(TripCreate, self).form_valid(form)


class AcceptDecline(UpdateView):
    model = Trip
    fields = ['invited', 'attending', 'declined']
    template_name = 'user/home.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(AcceptDecline, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse('home')

    def form_valid(self, form):
        trip = Trip.objects.get(pk=form.data['trip'])
        if form.data['action'] == 'attending':
            camper = Camper.objects.get(pk=form.data['attending'])
            trip.attending.add(camper)
            trip.invited.remove(camper)
        else:
            camper = Camper.objects.get(pk=form.data['declined'])
            trip.declined.add(camper)
            trip.invited.remove(camper)
        trip.save()
        return super(AcceptDecline, self).form_valid(form)