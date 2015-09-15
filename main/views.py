import datetime
import json
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import render, render_to_response, redirect
from django.template import RequestContext
from django.utils.decorators import method_decorator
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View, CreateView, DetailView, UpdateView
from main.apicalls import make_user_lat_lng, get_location_zip
from main.forms import CamperCreateForm
from main.helpers import marker_set, get_or_send_email
from main.models import Camper, Trip, Location, Review, Message, Photo, \
    UnregisteredUser


class Home(View):
    """Homepage View. Different templates depending if user is logged in or not"""

    def get(self, request, *arg):
        """if user is logged in, send to homepage"""
        if request.user.pk is not None:
            """Gather all locations and seralize the data"""
            markers = marker_set(request)
            invited_markers = markers[0]
            upcoming_markers = markers[1]
            past_markers = markers[2]
            context = {'camper': request.user.camper,
                       'locations': Location.objects.select_related().all(),
                       'all_locations': serializers.serialize('json', []),
                       'invited_locations': mark_safe(invited_markers),
                       'upcoming_locations': mark_safe(upcoming_markers),
                       'past_locations': mark_safe(past_markers),
                       }
            return render_to_response(template_name='user/home.html',
                                      context=context,
                                      context_instance=RequestContext(request))

        # if not logged in, send to default page
        else:
            self.all_locations = serializers.serialize('json',
                                                       Location.objects.all())
            context = {'photos': Photo.objects.all()[:19],
                       'reviews': Review.objects.all()[:9]
                       }
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
            make_user_lat_lng(camper, zipcode=data['zip'])
            camper.user = user
            camper.save()
            try:
                unregistered_user = UnregisteredUser.objects.get(
                    email=data['email'])
                for trip in unregistered_user.invited.all():
                    trip.invited.add(camper)
                    trip.save()
                unregistered_user.delete()
            except:
                pass
            user = authenticate(username=request.POST['username'],
                                password=request.POST['password1'])
            login(request, user)

            return HttpResponseRedirect(reverse('home'))

    else:
        form = CamperCreateForm()

    return render(request, 'user/register.html',
                  {'form': form})


class AllLocations(View):
    def get(self, request, *arg):
        markers = marker_set(request)
        invited_markers = markers[0]
        upcoming_markers = markers[1]
        past_markers = markers[2]
        context = {'camper': request.user.camper,
                   'locations': Location.objects.select_related().all(),
                   'all_locations': serializers.serialize('json', []),
                   'invited_locations': mark_safe(invited_markers),
                   'upcoming_locations': mark_safe(upcoming_markers),
                   'past_locations': mark_safe(past_markers),
                   }
        return render_to_response(template_name='location/all.html',
                                  context=context,
                                  context_instance=RequestContext(request))


class LocationDetail(DetailView):
    """Detail view for a location"""
    model = Location
    template_name = 'location/detail.html'

    def get_context_data(self, **kwargs):
        context = super(LocationDetail, self).get_context_data(**kwargs)
        try:
            context['photos'] = self.object.photos.all()
        except:
            context['photos'] = None
        return context


class LocationCreate(CreateView):
    model = Location
    fields = ('name',)
    template_name = "location/create.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LocationCreate, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse('location_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        form.is_valid()
        data = form.data.dict()
        get_location_zip(location=form.instance, lat=data['lat'],
                     lng=data['lng'])
        return super(LocationCreate, self).form_valid(form)


class ReviewCreate(CreateView):
    model = Review
    fields = ('content',)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ReviewCreate, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ReviewCreate, self).get_context_data(**kwargs)
        context['location'] = Location.objects.get(pk=self.kwargs['pk'])
        return context

    def get_success_url(self):
        return reverse(viewname='location_detail',
                       kwargs={'pk': self.kwargs['pk']})

    def form_valid(self, form):
        """Make the owner of the trip the user who created it"""
        if form.is_valid():
            review = form.instance
            review.content = form.cleaned_data['content']
            review.location = Location.objects.get(pk=self.kwargs['pk'])
            review.owner = self.request.user.camper
            review.save()
        return super(ReviewCreate, self).form_valid(form)


class TripDetail(DetailView):
    model = Trip
    template_name = 'trip/detail.html'

    def get_context_data(self, **kwargs):
        """
        Add extra content to determine if the trip is over or not and pass
        pictures to the view
        """
        context = super(TripDetail, self).get_context_data(**kwargs)
        if self.object.end_date > datetime.date.today():
            context['upcoming'] = True
        else:
            context['upcoming'] = False
        context['photos'] = self.object.photos.all()
        return context


class TripCreate(CreateView):
    model = Trip
    fields = (
        'start_date', 'end_date', 'title', 'description', 'max_capacity',)
    template_name = "trip/create.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(TripCreate, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(TripCreate, self).get_context_data(**kwargs)
        context['location'] = Location.objects.get(pk=self.kwargs['pk'])
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


class MessageCreate(CreateView):
    model = Message
    fields = ('content',)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(MessageCreate, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(MessageCreate, self).get_context_data(**kwargs)
        context['trip'] = Trip.objects.get(pk=self.kwargs['pk'])
        return context

    def get_success_url(self):
        return reverse(viewname='trip_detail', kwargs={'pk': self.kwargs['pk']})

    def form_valid(self, form):
        """Make the owner of the trip the user who created it"""
        if form.is_valid():
            message = form.instance
            message.content = form.cleaned_data['content']
            message.trip = Trip.objects.get(pk=self.kwargs['pk'])
            message.owner = self.request.user.camper
            message.save()
        return super(MessageCreate, self).form_valid(form)


def get_markers(request):
    query_string = request.GET.dict()
    if int(query_string['zoom']) >= 7:
        locations = Location.objects.filter(
            lat__lte=float(query_string['n']),
            lat__gte=float(query_string['s']),
            lng__lte=float(query_string['e']),
            lng__gte=float(query_string['w']))
        locations = serializers.serialize('json', locations)
        return JsonResponse(locations, safe=False)
    else:
        return HttpResponse(status=204)


@csrf_exempt
def image_upload(request, pk):
    data = json.loads(request.body.decode('utf8'))
    if data['sites']:
        if data['type'] == 'location':
            location = Location.objects.get(pk=pk)
            for picture in data['sites']:
                photo = Photo.objects.create(
                    location=location,
                    thumbnail=picture['thumbnail'],
                    url=picture['url'])
                photo.save()
            return HttpResponse(status=201)
        if data['type'] == 'trip':
            trip = Trip.objects.get(pk=pk)
            for picture in data['sites']:
                photo = Photo.objects.create(
                    trip=trip,
                    thumbnail=picture['thumbnail'],
                    url=picture['url'])
                photo.save()
            return HttpResponse(status=201)
        else:
            return HttpResponse(status=400)
    else:
        return HttpResponse(status=204)

def invite(request):
    form = request.POST
    form = form.dict()
    trip = Trip.objects.get(pk=form['trip'])
    if form['type'] == 'email':
        get_or_send_email(address=form['value'], first=form['first_name'], trip=trip)
    else:
        camper = Camper.objects.filter(user__username=form['value'])[0]
        trip.invited.add(camper)
    trip.save()
    return redirect('trip_detail', pk=trip.pk)


def user_login(request):
    """
    Function to login users
    :param request:
    :return:
    """
    context = RequestContext(request)
    username = request.POST['username']
    password = request.POST['password']

    # Attempt to validate the user
    user = authenticate(username=username, password=password)
    # If User is valid
    if user:
        # Make sure user is active
        if user.is_active:
            # log in the user and return to the homepage
            login(request, user)
            return redirect('home')
        else:
            # An inactive account was used - no logging in!
            return HttpResponse("Your account is disabled.")
    else:
        # Bad login details were provided. So we can't log the user in.
        return HttpResponse("Sorry, we could not log you in. Please try again!")