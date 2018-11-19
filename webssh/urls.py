from django.urls import path
from webssh.views import WebSSH

urlpatterns = [
    path(r'', WebSSH.as_view(), name="webssh"),
]
