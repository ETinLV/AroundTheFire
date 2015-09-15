from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import TemplateView
import main
from main.views import TripCreate, Home, TripDetail, LocationDetail, \
    LocationCreate, AcceptDecline, ReviewCreate, MessageCreate, AllLocations
from django.contrib.auth import views as auth_views


urlpatterns = [
    # Default Url
    url(r'^$', Home.as_view(), name="home"),

    # Admin Urls
    url(r'^logout', auth_views.logout, {'next_page': '/'},  name='logout'),
    url(r'^login', main.views.user_login, name='login'),
    url(r'^admin/', include(admin.site.urls)),

    #User Urls
    url(r'^user/register', main.views.create_camper, name='register'),

    # Trip Urls
    url(r'^trip/accept_decline/(?P<pk>[0-9]+)/$', AcceptDecline.as_view(), name="accept_decline"),
    url(r'^trip/create/(?P<pk>[0-9]+)/$', TripCreate.as_view(), name="trip_create"),
    url(r'^trip/(?P<pk>[0-9]+)/$', TripDetail.as_view(), name="trip_detail"),
    url(r'^trip/message/(?P<pk>[0-9]+)/$', MessageCreate.as_view(), name="message_create"),
    url(r'^trip/update/(?P<pk>[0-9]+)/$', AcceptDecline.as_view(), name="accept_decline"),
    url(r'^trip/invite/$', main.views.invite, name="invite"),

    #Location Urls
    url(r'^locations/$', AllLocations.as_view(), name="locations_all"),
    url(r'^location/(?P<pk>[0-9]+)/$', LocationDetail.as_view(), name="location_detail"),
    url(r'^location/new/$', LocationCreate.as_view(), name="location_create"),
    url(r'^location/review/(?P<pk>[0-9]+)/$', ReviewCreate.as_view(), name="review_create"),
    url(r'^get_markers/', main.views.get_markers, name="get_markers"),

    #Image Url
    url(r'^image/upload/(?P<pk>[0-9]+)/$', main.views.image_upload, name="image_upload"),
]
