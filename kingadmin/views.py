from django.shortcuts import render,redirect
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from kingadmin.from_handle import create_dynamic_model_form
from kingadmin import app_setup
from django.db.models import Q
import json

#程序已启动就自动执行
app_setup.kingadmin_auto_discover()
from kingadmin.sites import site

def app_index(request):
    return render(request,'kingadmin/app_index.html',{'site':site})

def acc_login(request):
    error_msg = ''
    if request.method == "POST":
        username = request.POST.get('username',None)
        password = request.POST.get('password',None)
        user = authenticate(username=username,password=password)
        if user:
            login(request,user)
            return redirect(request.GET.get('next','/kingadmin/'))
        else:
            error_msg = "用户名或密码错误"
    return render(request,'kingadmin/login.html',{'error_msg':error_msg})

def acc_logout(request):
    logout(request)
    return redirect('/login/')

def get_filter_result(request,querysets):
    filter_conditions = {}
    for key,val in request.GET.items():
        if key in ('page','_o','_q'):continue
        if val:
            filter_conditions[key] = val
    return querysets.filter(**filter_conditions),filter_conditions

@login_required
def table_obj_list(request,app_name,model_name):
    """
    取出指定model里的数据返回给前端
    :param request:
    :param app_name:
    :param model_name:
    :return:
    """
    admin_class = site.enable_admins[app_name][model_name]
    if request.method == "POST":
        # 获取action
        selected_action = request.POST.get("action")
        # 获取选中的id
        selected_ids = request.POST.get("selected_ids")
        selected_ids = json.loads(selected_ids)
        if not selected_action:
            # 选中的数据（selected_ids）都删除
            if selected_ids:
                admin_class.model.objects.filter(id__in=selected_ids).delete()
        else:
            # 选中所有选中id的对象
            selected_objs = admin_class.model.objects.filter(id__in=selected_ids)
            admin_action_func = getattr(admin_class, selected_action)
            # 把数据返回到前端
            response = admin_action_func(request, selected_objs)
            if response:
                return response

    querysets = admin_class.model.objects.get_queryset().order_by('-id')
    querysets,filter_conditions = get_filter_result(request,querysets)
    querysets,sorted_column = get_orderby_result(request,querysets,admin_class)
    paginator = Paginator(querysets,admin_class.list_per_page)
    page = request.GET.get('page')
    try:
        querysets = paginator.page(page)
    except PageNotAnInteger:
        querysets = paginator.page(1)
    except EmptyPage:
        querysets = paginator.page(paginator.num_pages)
    admin_class.filter_conditions = filter_conditions
    return render(request,'kingadmin/table_obj_list.html',locals())

def get_orderby_result(request,querysets,admin_class):
    """
    排序
    :param request:
    :param querysets:
    :param admin_class:
    :return:
    """
    # 记录按照哪一个字段排序
    current_ordered_column = {}
    orderby_index = request.GET.get('_o')
    if orderby_index:
        orderby_key = admin_class.list_display[abs(int(orderby_index))]
        current_ordered_column[orderby_key] = orderby_index
        if orderby_index.startswith('-'):
            orderby_key = '-' + orderby_key
        return querysets.order_by(orderby_key),current_ordered_column
    else:
        return querysets,current_ordered_column

def get_searched_result(request,querysets,admin_class):
    """
    搜索
    :param request:
    :param querysets:
    :param admin_class:
    :return:
    """
    search_key = request.GET.get('_q')
    if search_key:
        q = Q()
        q.connector = 'OR'
        for search_field in admin_class.search_fields:
            q.children.append("%s__contains"%search_field,search_key)
        return querysets.filter(q)
    return querysets

@login_required
def table_obj_change(request,app_name,model_name,id):
    admin_class = site.enable_admins[app_name][model_name]
    model_form = create_dynamic_model_form(admin_class,form_add=False)
    obj = admin_class.model.objects.get(id=id)
    # 修改
    if request.method == "GET":
        form_obj = model_form(instance=obj)
    else:
        form_obj = model_form(instance=obj,data=request.POST)
        if form_obj.is_valid():
            form_obj.save()
            return redirect("/kingadmin/%s/%s"%(app_name,model_name))
    return render(request,"kingadmin/table_obj_change.html",locals())

@login_required
def table_obj_add(request,app_name,model_name):
    """kingadmin数据添加"""
    admin_class = site.enable_admins[app_name][model_name]
    model_form = create_dynamic_model_form(admin_class,form_add=True)

    if request.method == 'GET':
        form_obj = model_form()
    elif request.method == 'POST':
        form_obj = model_form(data=request.POST)
        if form_obj.is_valid():
            form_obj.save()
            # 跳转到的页面
            return redirect("/kingadmin/%s/%s/" % (app_name, model_name))
    return render(request, 'kingadmin/table_obj_add.html', locals())

@login_required
def table_obj_delete(request,app_name,model_name,id):
    admin_class = site.enable_admins[app_name][model_name]
    obj = admin_class.model.objects.get(id=id)
    return render(request,'kingadmin/table_obj_delete.html',locals())

@login_required
def table_list(request,app_name):
    table_list = []
    if app_name in site.enable_admins:
        for model_name in site.enable_admins[app_name]:
            table_list.append(model_name)
    return render(request,'kingadmin/table_list.html',locals())
