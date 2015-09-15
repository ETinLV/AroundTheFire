import json
import requests
from main.apikeys import googlekey, trailkey, weatherkey
from main.models import Location, Photo


def make_address(object, zip=None, lat=None, lng=None):
    """
    Takes an object and either a zip code or lat/lng value and creates the other
    data. Also saves the nearest city
    """
    # If zip code given, add lat,lng and city
    if zip:
        response = requests.get(
            'https://maps.googleapis.com/maps/api/geocode/json?address={zip}&components=country:US&key={googlekey}'.format(
                zip=zip, googlekey=googlekey))
        data = json.loads(response.content.decode('utf-8'))
        data = data['results'][0]
        object.zip = zip
        object.lat = data['geometry']['location']['lat']
        object.lng = data['geometry']['location']['lng']
        object.city = data['address_components'][1]['short_name']
        object.save()
        return object
    # If lat/lng given, return zip and city
    else:
        response = requests.get(
            'https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lng}&key={googlekey}'.format(
                lat=lat, lng=lng, googlekey=googlekey))
        data = json.loads(response.content.decode('utf-8'))
        try:
            data = data['results'][0]
            object.city = data['address_components'][1]['short_name']
            try:
                object.zip = data['address_components'][5]['short_name']
                object.lat = lat
                object.lng = lng
            except:
                object.zip = None
                object.lat = lat
                object.lng = lng
            object.save()
            return object
        except:
            pass


def call_trail_api(lat='0', lng='0', radius=500, limit=1000):
    """Calls the trail_api and returns campsites"""
    response = requests.get(
        "https://trailapi-trailapi.p.mashape.com/?lat={lat}&limit={limit}&lon={lng}&q[activities_activity_type_name_eq]=camping&q[country_cont]=united+states&radius={radius}".format(
            lat=lat, limit=limit, lng=lng, radius=radius),
        headers={
            "X-Mashape-Key": trailkey,
            "Accept": "text/plain"
        })
    data = json.loads(response.content.decode('utf-8'))
    return data


def api_create_locations(lat=None, lng=None):
    """adds locations from the trail api to the location database"""
    for object in call_trail_api(lat=lat, lng=lng)['places']:
        location, created = Location.objects.get_or_create(api_id=object['unique_id'])
        location.lat = object['lat']
        location.lng = object['lon']
        make_address(location, lat=location.lat, lng=location.lng)
        if created:
            for image in object['activities']:
                if image['thumbnail']:
                    Photo.objects.get_or_create(thumbnail=image['thumbnail'], url=image['thumbnail'], location=location)
        location.name = object['name']
        location.save()


def get_weather(lat, lng):
    response = requests.get(
        "http://api.wunderground.com/api/{weatherkey}/forecast/geolookup/conditions/q/{lat},{lng}.json".format(
            weatherkey=weatherkey, lat=lat, lng=lng))
    data = json.loads(response.content.decode('utf-8'))
    return data


