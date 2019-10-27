from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
import json
from django.views.decorators.csrf import csrf_protect

@csrf_protect
def index(request):
    if request.method == 'POST':
        json_data = json.loads(request.body) # request.raw_post_data w/ Django < 1.4
    try:
        data = json_data['data']
    except KeyError:
        HttpResponseServerError("Malformed data!")
    print("Got json data!")
    HttpResponse("Got json data")
