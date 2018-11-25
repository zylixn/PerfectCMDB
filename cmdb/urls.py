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
from django.conf.urls import url
from cmdb.views import IndexView,AssetList,ServerDetail,AssetReport,NewAssetApprovalZoneList

urlpatterns = [
    url('',IndexView.as_view(),name="crm_index"),
    url('servers/',AssetList.as_view(),name="server_list"),
    url('newassets/',NewAssetApprovalZoneList.as_view(),name="newasset_list"),
    url('servers/<int:pk>/',ServerDetail.as_view(),name="serverdetail"),
    url('asset/report/',AssetReport.as_view(),name="asset_report_interface"),
]
