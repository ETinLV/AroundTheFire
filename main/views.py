from django.http import HttpResponse
import json
from django.shortcuts import render

# Create your views here.
from django.views.generic import View
import requests
from main.apikeys import trailkey, weatherkey

def call_api(location):
    response = requests.get(
        "https://trailapi-trailapi.p.mashape.com/?q[activities_activity_type_name_eq]=camping&q[city_cont]={}".format(
            location),
        headers={
            "X-Mashape-Key": trailkey,
            "Accept": "text/plain"
                })
    data = json.loads(response.content.decode('utf-8'))


    response = requests.get(
    "http://api.wunderground.com/api/{}/conditions/forecast/q/CA/{}.json".format(trailkey,
        location))
    data = json.loads(response.content.decode('utf-8'))
    return data


"""quick test to make sure the api call is working. it is."""
class MyView(View):
    def get(self, request):
        results = call_api('san diego')
        return HttpResponse(results)

