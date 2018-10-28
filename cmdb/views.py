from django.shortcuts import render,HttpResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import AccessMixin
from django.utils.translation import activate
from django.core.exceptions import  PermissionDenied
from django.contrib.auth.views import redirect_to_login
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from cmdb.models import ServerInfor
from django.http import JsonResponse
from django.views.generic import TemplateView
from django_redis import get_redis_connection
from django.utils.safestring import mark_safe
from cmdb.core import AssetHandler
from cmdb import utils
import json

class LoginRequiredMixin(AccessMixin):
    """
    CBV mixin which verifies that the current user is authenticated.
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return self.handle_no_permission()
        activate(request.LANGUAGE_CODE.replace('-','_'))
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)

    def handle_no_permission(self):
        if self.raise_exception and self.request.user.is_authenticated():
            raise PermissionDenied(self.get_permission_denied_message())
        return redirect_to_login(self.request.get_full_path(), self.get_login_url(), self.get_redirect_field_name())

class IndexView(View):
    def get(self,request):
        return render(request,'common/index.html')

class ServerList(ListView):
    model = ServerInfor
    template_name = 'cmdb/resource.html'
    permission_required = 'cmdb.can_view_serverinfo'
    raise_exception = True

    def get_context_data(self, **kwargs):
        context = super(ServerList, self).get_context_data(**kwargs)
        context['serverlist'] = ServerInfor.objects.all()
        return context

class ServerDetail(DetailView):
    model = ServerInfor
    template_name = "cmdb/serverinfodetail.html"

    def get_context_data(self, **kwargs):
        context = super(ServerDetail, self).get_context_data(**kwargs)
        return context

    def post(self,request,*args,**kwargs):
        if request.is_ajax():
            print("*"*10,request.body)
            #data = json.loads(request.body)
            obj_id = request.POST.get('id')
            choice = request.POST.get('choice')
            #print("obj_id:%s---choice:%s"%(obj_id,choice))
            conn = get_redis_connection("default")
            msg = conn.hget("ServerList",obj_id)
            if not msg:
                # 如果redis里面没有对应设备的信息,则进行相应的配置采集
                pass
            else:
                pass
            msg = "It's a test"
            return JsonResponse({'status':True,'message':msg})

class AssetReport(TemplateView):

    def post(self,request,*args,**kwargs):
        asset_data = request.POST.get("asset_data")
        if asset_data:
            asset_data = json.dumps(asset_data)
            print("Recv data ",asset_data)
            asset_id = asset_data.get("asset_id")
            asset_handler = AssetHandler(request)
            if asset_id:
                # 将带有id的资产信息入到相应的表里面
                if asset_handler.data_is_available():
                    asset_handler.handler_asset()
                return HttpResponse(json.dumps(asset_handler.response))
            else:
                # 将没有id的资产入到待审批的表里面
                res = asset_handler.get_asset_id_by_sn()
                return HttpResponse(json.dumps(res))

    @csrf_exempt
    @utils.token_required
    def dispatch(self, request, *args, **kwargs):
        return super(AssetReport, self).dispatch(*args,**kwargs)



