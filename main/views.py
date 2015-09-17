import datetime
import json

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import render_to_response, redirect

from django.template import RequestContext

from django.utils.decorators import method_decorator

from django.utils.safestring import mark_safe

from django.views.decorators.csrf import csrf_exempt

from django.views.generic import View, CreateView, DetailView, UpdateView

from main.api_calls import make_user_lat_lng, get_location_zip
from main.forms import CamperCreateForm
from main.helpers import trip_marker_set, get_or_send_email, \
    convert_unregistered_user
from main.models import Camper, Trip, Location, Review, Message, Photo


class Index(View):
    def get(self, request, *arg):
        """Determine if user is logged in and return the correct homepage"""
        if request.user.pk is not None:
            return redirect('user_home')

        # if not logged in, send to default page
        else:
            context = {'photos': Photo.objects.all()[:19],
                       'reviews': Review.objects.all()[:9]
                       }
            return render_to_response(template_name='default.html',
                                      context=context,
                                      context_instance=RequestContext(request))


class UserHome(View):
    """
    User Homepage
    """

    @method_decorator(login_required)
    def get(self, request, *arg):
        """Gather the user's trips and return the homepage"""
        markers = trip_marker_set(request)
        invited_markers = markers['invited']
        upcoming_markers = markers['upcoming']
        past_markers = markers['past']
        context = {'camper': request.user.camper,
                   'invited_locations': mark_safe(invited_markers),
                   'upcoming_locations': mark_safe(upcoming_markers),
                   'past_locations': mark_safe(past_markers),
                   }
        return render_to_response(template_name='user/home.html',
                                  context=context,
                                  context_instance=RequestContext(request))


def create_camper(request):
    """Accept POST data and register a camper"""

    form = CamperCreateForm(request.POST)
    if form.is_valid():

        # Create the camper
        data = form.cleaned_data
        user = form.save()
        camper = Camper()

        # Call function to add zip and city
        make_user_lat_lng(camper, zipcode=data['zip'])

        # Save the Camper
        camper.user = user
        camper.save()

        # Call function to see if previously unregistered user
        convert_unregistered_user(data, camper)

        # Login the new user
        user = authenticate(username=request.POST['username'],
                            password=request.POST['password1'])
        login(request, user)

        return HttpResponseRedirect(reverse('home'))

    else:
        return redirect('home')


class AllLocations(View):
    """View for users to see all locations in the database"""

    def get(self, request, *arg):
        """Gather the user's trips and return the all locations page"""

        markers = trip_marker_set(request)
        invited_markers = markers['invited']
        upcoming_markers = markers['upcoming']
        past_markers = markers['past']
        context = {'camper': request.user.camper,
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
        context['photos'] = self.object.photos.all()
        return context


class LocationCreate(CreateView):
    """ Create location View"""

    model = Location
    fields = ('name',)
    template_name = 'location/create.html'

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
    """View to Create a Review"""

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
        """Create the Review and add current user as the creator"""

        if form.is_valid():
            review = form.instance
            review.content = form.cleaned_data['content']
            review.location = Location.objects.get(pk=self.kwargs['pk'])
            review.owner = self.request.user.camper
            review.save()
        return super(ReviewCreate, self).form_valid(form)


class TripDetail(DetailView):
    """Trip Detail View"""

    model = Trip
    template_name = 'trip/detail.html'

    def get_context_data(self, **kwargs):
        """
        Add extra content to determine if the trip is over and pass
        pictures to the template
        """
        context = super(TripDetail, self).get_context_data(**kwargs)
        # Determine if trip is upcoming
        if self.object.end_date > datetime.date.today():
            context['upcoming'] = True
        else:
            context['upcoming'] = False
        # Add Photos
        context['photos'] = self.object.photos.all()
        return context


class TripCreate(CreateView):
    """Trip Create View"""

    model = Trip
    fields = (
        'start_date', 'end_date', 'title', 'description', 'max_capacity',
        "location")
    template_name = 'trip/create.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(TripCreate, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(TripCreate, self).get_context_data(**kwargs)
        return context

    def get_success_url(self):
        return reverse('trip_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        """Make the owner of the trip the user who created it"""
        form.instance.owner = self.request.user.camper
        form.instance.location = form.cleaned_data['location']
        return super(TripCreate, self).form_valid(form)


class AcceptDecline(UpdateView):
    """Update the trip if a Camper accepts or declines and invite"""
    model = Trip
    fields = ['invited', 'attending', 'declined']

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(AcceptDecline, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse('home')

    def form_valid(self, form):
        # Determine if the user has accepted or declined
        trip = Trip.objects.get(pk=form.data['trip'])
        if form.data['action'] == 'attending':
            # If accepted, add to the attending and remove from invited
            camper = Camper.objects.get(pk=form.data['attending'])
            trip.attending.add(camper)
            trip.invited.remove(camper)
        else:
            # If declined, add to declined and removed from invited
            camper = Camper.objects.get(pk=form.data['declined'])
            trip.declined.add(camper)
            trip.invited.remove(camper)
        trip.save()
        return super(AcceptDecline, self).form_valid(form)


class MessageCreate(CreateView):
    """Create a message"""
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
        """Make the owner of the message the user who created it
        and add the trip it is related to"""
        if form.is_valid():
            message = form.instance
            message.content = form.cleaned_data['content']
            message.trip = Trip.objects.get(pk=self.kwargs['pk'])
            message.owner = self.request.user.camper
            message.save()
        return super(MessageCreate, self).form_valid(form)


def get_markers(request):
    """Return markers in a map bounds box."""

    query_string = request.GET.dict()
    # Only Return objects if the zoomed in far enough
    if int(query_string['zoom']) >= 7:
        # Find all locations within the bound box
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
    """ Add a photo object to the database

    Accepts a JSON dict with the photo object and the trip or location the image
    relates to. Creates the photo object.
    """

    data = json.loads(request.body.decode('utf8'))
    # Check if something was uploaded
    if data['sites']:
        if data['type'] == 'location':
            location = Location.objects.get(pk=pk)
            # Create each photo object
            for picture in data['sites']:
                photo = Photo.objects.create(
                    location=location,
                    thumbnail=picture['thumbnail'],
                    url=picture['url'])
                photo.save()
            return HttpResponse(status=201)
        if data['type'] == 'trip':
            trip = Trip.objects.get(pk=pk)
            # Create each photo object
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
    """ Add user to the invited list

    Accept an email or username, if email, determine if that email is
    registered, if not update/create an UnregisteredUser object, if so add that
    user to the invited list. If username is given, add that user to the
    invited user list
    """

    form = request.POST
    form = form.dict()
    trip = Trip.objects.get(pk=form['trip'])
    if form['type'] == 'email':
        get_or_send_email(address=form['value'], first=form['first_name'],
                          trip=trip)
    else:
        camper = Camper.objects.filter(user__username=form['value'])[0]
        trip.invited.add(camper)
    trip.save()
    return redirect('trip_detail', pk=trip.pk)


def user_login(request):
    """
    Log users in or send to error page
    """

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
