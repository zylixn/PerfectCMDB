from django.shortcuts import render
from cmdb.models import *

def index(request):
    print("*" * 10)
    param = {
        'user':'lixn',
        'password':'lixn'
    }
    return render(request,"index.html",context=param)

