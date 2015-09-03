"""aroundthefire URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import TemplateView
import main
from main.views import TripCreate, Home, TripDetail, LocationDetail, \
    LocationCreate
from django.contrib.auth import views as auth_views


urlpatterns = [
    url(r'^login', auth_views.login, {'template_name': 'user/login.html', 'extra_context': {'next': '/'}}, name='login'),
    url(r'^trip/create', TripCreate.as_view(), name="trip_create"),
    url(r'^trip/(?P<pk>[0-9]+)/$', TripDetail.as_view(), name="trip_detail"),
    url(r'^location/create/\((?P<lat>[0-9.]+), (?P<lng>\-[0-9.]+)', LocationCreate.as_view(), name="location_create"),
    url(r'^location/(?P<pk>[0-9]+)/$', LocationDetail.as_view(), name="location_detail"),
    url(r'^location/new/$', LocationCreate.as_view(), name="location_create"),
    url(r'^user/register', main.views.create_camper, name='register'),
    url(r'^admin/', include(admin.site.urls)),
    # url(r'^apitest', MyView.as_view()),
    url(r'^$', Home.as_view(), name="home"),
]

#TODO Clean this up.