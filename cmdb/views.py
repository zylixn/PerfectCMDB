from django.shortcuts import render,HttpResponse,redirect
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import AccessMixin
from django.utils.translation import activate
from django.core.exceptions import  PermissionDenied
from django.contrib.auth.views import redirect_to_login
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from cmdb.models import ServerInfor,Asset,NewAssetApprovalZone
from django.http import JsonResponse,Http404
from django.views.generic import TemplateView
from django_redis import get_redis_connection
from django.utils.safestring import mark_safe
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from cmdb.core import AssetHandler
from cmdb.admin import AssetAdmin,NewAssetApprovalZoneAdmin
from cmdb import utils
import datetime
import json
import traceback
import re

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

class AssetList(ListView):
    model = Asset
    template_name = 'cmdb/asset_list.html'
    permission_required = 'cmdb.can_view_serverinfo'
    raise_exception = True

    def get_context_data(self, *, object_list=None, **kwargs):
        filter_conditions = {}
        sorted_column = None
        context = super(AssetList, self).get_context_data(**kwargs)
        querysets = Asset.objects.get_queryset().order_by('id')
        try:
            print("1queryset:", querysets)
            querysets = utils.search_by(self.request, querysets, AssetAdmin)
            print("2queryset:",querysets)
            querysets, filter_conditions = utils.get_filter_result(self.request, querysets)
            querysets, sorted_column = utils.get_orderby_result(self.request, querysets, AssetAdmin)
            paginator = Paginator(querysets, AssetAdmin.list_per_page)
            page = self.request.GET.get('page')
            try:
                querysets = paginator.page(page)
            except PageNotAnInteger:
                querysets = paginator.page(1)
            except EmptyPage:
                querysets = paginator.page(paginator.num_pages)
        except Exception as e:
            traceback.print_exc()

        # AssetAdmin.filter_conditions = filter_conditions
        context['assets'] = querysets
        context['sorted_column'] = sorted_column
        context['model'] = Asset
        context['list_filter'] = AssetAdmin.list_filter
        context['list_display'] = AssetAdmin.list_display
        context['search_fields'] = AssetAdmin.search_fields
        context['filter_conditions'] = filter_conditions
        # print("model:%s,admin_class:%s"%(type(Asset),type(AssetAdmin)))
        return context

    def post(self,request):
        IDS = request.POST.get('IDS')
        print("IDS:",IDS)
        arr = IDS.split('-')
        if arr:
            Asset.objects.filter(id__in=arr).delete()
        return redirect('/cmdb/servers/')

class NewAssetApprovalZoneList(ListView):
    model = NewAssetApprovalZone
    template_name = 'cmdb/newasset_list.html'
    permission_required = 'cmdb.can_view_serverinfo'
    raise_exception = True

    def get_context_data(self, *, object_list=None, **kwargs):
        filter_conditions = {}
        sorted_column = None
        context = super(NewAssetApprovalZoneList, self).get_context_data(**kwargs)
        querysets = NewAssetApprovalZone.objects.get_queryset().order_by('id')
        try:
            print("1queryset:", querysets)
            querysets = utils.search_by(self.request, querysets, NewAssetApprovalZoneAdmin)
            print("2queryset:",querysets)
            querysets, filter_conditions = utils.get_filter_result(self.request, querysets)
            querysets, sorted_column = utils.get_orderby_result(self.request, querysets, AssetAdmin)
            paginator = Paginator(querysets, AssetAdmin.list_per_page)
            page = self.request.GET.get('page')
            try:
                querysets = paginator.page(page)
            except PageNotAnInteger:
                querysets = paginator.page(1)
            except EmptyPage:
                querysets = paginator.page(paginator.num_pages)
        except Exception as e:
            traceback.print_exc()
        context['assets'] = querysets
        context['sorted_column'] = sorted_column
        context['model'] = NewAssetApprovalZone
        context['list_filter'] = NewAssetApprovalZoneAdmin.list_filter
        context['list_display'] = NewAssetApprovalZoneAdmin.list_display
        context['search_fields'] = NewAssetApprovalZoneAdmin.search_fields
        context['filter_conditions'] = filter_conditions
        return context

    def post(self,request):
        result = {"error": ""}
        asset_id = request.POST.get("id")
        asset = dict()
        m = re.search(r'(\D+)(\d+)',asset_id)
        if m:
            asset_id = m.group(2)
        if asset_id:
            # 将asset_id对应的对象状态改成已审批
            newasset = NewAssetApprovalZone.objects.get(id=asset_id)
            newasset.approved = True
            newasset.approved_by = request.user
            newasset.approved_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            newasset.save()
            asset = {
                    "sn":newasset.sn,
                    "asset_type":newasset.asset_type,
                    "manufactory":newasset.manufactory,
            }
            obj = Asset(**asset)
            obj.save()
        else:
            result = {"error":"appoval failed"}
            #return JsonResponse(result)
        return JsonResponse(result)
    
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(NewAssetApprovalZoneList, self).dispatch(request, *args, **kwargs)
        


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
