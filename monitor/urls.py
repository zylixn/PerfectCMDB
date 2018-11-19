from django.contrib import admin
from django.urls import path
from monitor.views import accpet_data

urlpatterns = [
    path('report/', accpet_data),
]