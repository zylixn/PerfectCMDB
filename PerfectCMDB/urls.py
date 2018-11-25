"""PerfectCMDB URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import url, include
from api import urls as api_urls

urlpatterns = [
    url(r'^api/',include(api_urls.router.urls)),
    url('admin/', admin.site.urls),
    url('cmdb/',include('cmdb.urls')),
    url('tasks/',include('tasks.urls')),
    url('monitor/',include('monitor.urls')),
    url('chat/',include('test_websocket.urls')),
    url('webssh/', include('webssh.urls')),
    url(r'^api-auth/', include('rest_framework.urls')),
]
