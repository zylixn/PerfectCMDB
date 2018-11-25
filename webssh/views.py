from django.shortcuts import render,render_to_response
from django.views.generic import TemplateView,ListView,View
from django.contrib.auth.mixins import LoginRequiredMixin
from cmdb.models import Asset,AssetGroup

class WebSSH(LoginRequiredMixin,View):

    def get(self,request):
        assetgroups = []
        assets = Asset.get_user_asset(request.user)
        for assetgroup in AssetGroup.objects.all():
            assetgroup.user_assets = [h for h in assets if h.group == assetgroup]
            if assetgroup.user_assets:
                assetgroups.append(assetgroup)
        cmdb_webssh_active = 'active'
        user = request.user

        return render_to_response('index_webssh.html',locals())

