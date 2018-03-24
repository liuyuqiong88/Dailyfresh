from django.http import *
from django.shortcuts import render

# Create your views here.
def index(request):


    return HttpResponse('首页')