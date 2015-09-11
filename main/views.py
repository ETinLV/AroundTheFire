import datetime
from itertools import chain
import json
import re
import cloudinary
from cloudinary.forms import cl_init_js_callbacks
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import render, render_to_response
from django.template import RequestContext
from django.utils.decorators import method_decorator
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View, CreateView, DetailView, UpdateView

from main.apicalls import make_address
from main.forms import CamperCreateForm, UploadFileForm
from main.helpers import marker_set
from main.models import Camper, Trip, Location, Photo, Review, Message


class Home(View):
    """Homepage View. Different templates depending if user is logged in or not"""

    def get(self, request, *arg):
        """if user is logged in, send to homepage"""
        if self.request.user.pk is not None:
            """Gather all locations and seralize the data"""
            markers = marker_set(request)
            self.invited_markers = markers[0]
            self.upcoming_markers = markers[1]
            self.past_markers = markers[2]
            context = {'camper': self.request.user.camper,
                       'locations': Location.objects.select_related().all(),
                       'all_locations': serializers.serialize('json', []),
                       'invited_locations': mark_safe(self.invited_markers),
                       'upcoming_locations': mark_safe(self.upcoming_markers),
                       'past_locations': mark_safe(self.past_markers),
                       }
            return render_to_response(template_name='user/home.html',
                                      context=context,
                                      context_instance=RequestContext(request))

        # if not logged in, send to default page
        else:
            self.all_locations = serializers.serialize('json',
                                                       Location.objects.all())
            context = {'locations': Location.objects.all(),
                       'all_locations': mark_safe(self.all_locations),
                       'invited_locations': serializers.serialize('json', []),
                       'upcoming_locations': serializers.serialize('json', []),
                       'past_locations': serializers.serialize('json', [])
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


class AllLocations(View):
    def get(self, request, *arg, **kwargs):
        self.all_locations = serializers.serialize('json',
                                                   Location.objects.all())
        context = {'locations': Location.objects.all(),
                   'all_locations': mark_safe(self.all_locations),
                   'invited_locations': serializers.serialize('json', []),
                   'upcoming_locations': serializers.serialize('json', []),
                   'past_locations': serializers.serialize('json', [])
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
        return reverse('home')

    def form_valid(self, form):
        make_address(object=form.instance, lat=form.data['lat'],
                     lng=form.data['lng'])
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


# TODO THis for messages!

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
        # TODO There HAS to be a better way than this....
        return context


class TripCreate(CreateView):
    model = Trip
    fields = (
        'start_date', 'end_date', 'title', 'description', 'max_capacity',
        'invited')
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


# def image_upload(request, pk):
#     form = UploadFileForm(request.POST)
#     cloudinary.forms.cl_init_js_callbacks(form, request)
#     location = Location.objects.get(pk=pk)
#     if request.method == 'POST':
#         if form.is_valid():
#             photo = Photo.objects.create(image=form.cleaned_data['image'])
#             image = form.cleaned_data['image']
#             photo.image = image
#             photo.location = location
#             photo.url = image.url
#             photo.save()
#             return HttpResponseRedirect('location/{}'.format(location.pk))
#     return render_to_response('location/upload.html',
#                               RequestContext(request, {'form': form, 'location': location}))

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
        return JsonResponse(None, safe=False)


@csrf_exempt
def image_upload(request, pk):
    data = json.loads(request.body.decode('utf8'))
    #TODO make this respond with the success url code
    return JsonResponse(None, safe=False)
