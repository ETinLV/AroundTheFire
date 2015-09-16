import json
import random

import requests

from main.api_keys import googlekey, trailkey
from main.models import Location, Photo


def get_location_zip(location, lat=None, lng=None):
    """
    Call the google API with a lat/lng pair to get the zipcode at that point

    :param location: location object
    :param lat: latitude
    :param lng: longitude
    :return: saved location
    """

    # Call the API with the lat/lng pair
    response = requests.get(
        'https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lng}&key={googlekey}'.format(
            lat=lat, lng=lng, googlekey=googlekey))
    data = json.loads(response.content.decode('utf-8'))
    data = data['results'][0]

    # Save the data
    location.city = data['address_components'][1]['short_name']
    location.lat = lat
    location.lng = lng

    # Rarely, google can not find a zipcode. Save these location with None.
    try:
        location.zip = data['address_components'][5]['short_name']
    except:
        location.zip = None
    location.save()
    return location


def make_user_lat_lng(user, zipcode):
    """
    Call the google API with a zipcode to get the centerpoint lat/lng

    :param user: user object
    :param zipcode: zipcode
    :return: saved user
    """

    # Call the google api with a zipcode
    response = requests.get(
        'https://maps.googleapis.com/maps/api/geocode/json?address={zip}&components=country:US&key={googlekey}'.format(
            zip=zipcode, googlekey=googlekey))
    data = json.loads(response.content.decode('utf-8'))
    data = data['results'][0]

    # Save the data
    user.lat = data['geometry']['location']['lat']
    user.lng = data['geometry']['location']['lng']
    user.city = data['address_components'][1]['short_name']
    user.save()
    return user


def call_trail_api(lat='0', lng='0', radius=500, limit=1000):
    """Call The Trail API and Return Campsites in Radius of location"""

    response = requests.get(
        "https://trailapi-trailapi.p.mashape.com/?lat={lat}&limit={limit}&lon={lng}&q[activities_activity_type_name_eq]=camping&q[country_cont]=united+states&radius={radius}".format(
            lat=lat, limit=limit, lng=lng, radius=radius),
        headers={
            "X-Mashape-Key": trailkey,
            "Accept": "text/plain"
        })
    data = json.loads(response.content.decode('utf-8'))
    return data


def api_create_locations(lat=None, lng=None, radius=500, limit=1000):
    """
    Add locations from the trail api to the location database

    :param lat: centerpoint latitude
    :param lng: centerpoint longitude
    :param radius: raidus
    :param limit: max campsites to create
    :return: None
    """

    # Create location object for each item returned
    for campsite in call_trail_api(
            lat=lat, lng=lng, radius=radius, limit=limit)['places']:
        location, created = Location.objects.get_or_create(
            api_id=campsite['unique_id'])
        location.lat = campsite['lat']
        location.lng = campsite['lon']
        get_location_zip(location, lat=location.lat, lng=location.lng)

        # If the location is new, add it's images to the Database
        if created:
            for image in campsite['activities']:
                if image['thumbnail']:
                    Photo.objects.get_or_create(thumbnail=image['thumbnail'],
                                                url=image['thumbnail'],
                                                location=location)
        location.name = campsite['name']
        location.save()


def make_locations(runs):
    """Create (runs) number of api calls to create locations"""

    for x in range(runs):
        api_create_locations(random.randint(29, 48), random.randint(-121, -69))
