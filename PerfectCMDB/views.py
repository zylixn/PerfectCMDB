from django.shortcuts import render
from cmdb.models import *

def index(request):

    return render(request,"index.html")

