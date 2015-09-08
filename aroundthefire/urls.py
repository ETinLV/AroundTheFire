from django.conf.urls import include, url
from django.contrib import admin
import main
from main.views import TripCreate, Home, TripDetail, LocationDetail, \
    LocationCreate, AcceptDecline, ReviewCreate
from django.contrib.auth import views as auth_views


urlpatterns = [
    url(r'^logout', auth_views.logout, {'next_page': '/'},  name='logout'),
    url(r'^login', auth_views.login, {'template_name': 'user/login.html', 'extra_context': {'next': '/'}}, name='login'),
    url(r'^trip/accept_decline/(?P<pk>[0-9]+)/$', AcceptDecline.as_view(), name="accept_decline"),
    url(r'^trip/create/(?P<pk>[0-9]+)/$', TripCreate.as_view(), name="trip_create"),
    url(r'^trip/(?P<pk>[0-9]+)/$', TripDetail.as_view(), name="trip_detail"),
    url(r'^location/create/\((?P<lat>[0-9.]+), (?P<lng>\-[0-9.]+)', LocationCreate.as_view(), name="location_create"),
    url(r'^location/(?P<pk>[0-9]+)/$', LocationDetail.as_view(), name="location_detail"),
    url(r'^location/new/$', LocationCreate.as_view(), name="location_create"),
    url(r'^location/review/(?P<pk>[0-9]+)/$', ReviewCreate.as_view(), name="review_create"),
    url(r'^user/register', main.views.create_camper, name='register'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', Home.as_view(), name="home"),
    url(r'^trip/update/(?P<pk>[0-9]+)/$', AcceptDecline.as_view(), name="accept_decline"),
    url(r'^location/upload/(?P<pk>[0-9]+)/$', main.views.image_upload, name="image_upload"),
]
