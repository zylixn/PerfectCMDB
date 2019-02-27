from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def accpet_data(request):
    if request.method == "POST":
        data = request.POST.get('asset_data')
    else:
        pass
    return JsonResponse({'status':'success','error':""})

