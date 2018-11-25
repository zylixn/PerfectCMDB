from django.conf.urls import url
from webssh.views import WebSSH

urlpatterns = [
    url(r'', WebSSH.as_view(), name="webssh"),
]
