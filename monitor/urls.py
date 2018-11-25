from django.contrib import admin
from django.conf.urls import url
from monitor.views import accpet_data

urlpatterns = [
    url('report/', accpet_data),
]