#_*_coding:utf-8_*_
__author__ = 'lixn'
import time,hashlib,json
from cmdb import models
from django.shortcuts import render,HttpResponse
from PerfectCMDB import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count,Q

def json_date_handler(obj):
    if hasattr(obj, 'isoformat'):
        return obj.strftime("%Y-%m-%d")


def json_datetime_handler(obj):
    if hasattr(obj, 'isoformat'):
        return obj.strftime("%Y-%m-%d %H:%M:%S")


def gen_token(username,timestamp,token):
    token_format = "%s\n%s\n%s" %(username,timestamp,token)
    #print('--->token format:[%s]'% token_format)
    obj = hashlib.md5()
    obj.update(token_format.encode())
    return obj.hexdigest()[10:17]


def token_required(func):
    def wrapper(*args,**kwargs):
        response = {"errors":[]}

        get_args = args[1].GET
        username = get_args.get("user")
        token_md5_from_client = get_args.get("token")
        timestamp = get_args.get("timestamp")
        if not username or not timestamp or not token_md5_from_client:
            response['errors'].append({"auth_failed":"This api requires token authentication!"})
            return HttpResponse(json.dumps(response))
        try:
            user_obj = models.UserProfile.objects.get(email=username)
            token_md5_from_server = gen_token(username,timestamp,user_obj.token)
            if token_md5_from_client != token_md5_from_server:
                response['errors'].append({"auth_failed":"Invalid username or token_id"})
            else:
                if abs(time.time() - int(timestamp)) > settings.TOKEN_TIMEOUT:# default timeout 120
                    response['errors'].append({"auth_failed":"The token is expired!"})
                else:
                    pass #print "\033[31;1mPass authentication\033[0m"

                print("\033[41;1m;%s ---client:%s\033[0m" %(time.time(),timestamp), time.time() - int(timestamp))
        except ObjectDoesNotExist as e:
            response['errors'].append({"auth_failed":"Invalid username or token_id"})
        if response['errors']:
            return HttpResponse(json.dumps(response))
        else:
            return  func(*args,**kwargs)
    return wrapper


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

def get_filter_result(request,querysets):
    filter_conditions = {}
    for key,val in request.GET.items():
        if key in ('page','_o','_q'):continue
        if val:
            filter_conditions[key] = val
    return querysets.filter(**filter_conditions),filter_conditions

def search_by(request,querysets,admin_form):
    search_str = request.GET.get("_q")
    if search_str:
        q_objs = []
        for q_field in admin_form.search_fields:
            q_objs.append("Q(%s__contains='%s')" %(q_field,search_str) )
        #print(" | ".join(q_objs) )
        return  querysets.filter(eval("|".join(q_objs)))
    return querysets