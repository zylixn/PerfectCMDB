from django import template
from django.utils.safestring import mark_safe
from django.db.models import Q
from cmdb import models
import datetime

register = template.Library()

@register.simple_tag()
def Menus():
    menus_all = {}
    # 获取全部的一级菜单
    menus = models.Menu.objects.filter(parent__isnull=True)
    for menu in menus:
        submenus = menu.menu_set.all()
        submenulist = []
        for submenu in submenus:
            submenulist.append(submenu)
        menus_all.update({menu: submenulist})
    return menus_all

@register.simple_tag
def build_table_row(obj,list_display,model):
    """生成一条记录的HTML element"""
    ele = ''
    if list_display:
        for index,column_name in enumerate(list_display):
            column_obj = model._meta.get_field(column_name)
            # 通过反射获取数据,两个参数,一个是object,一个是列名
            # column_data = getattr(obj,column_name)
            if column_obj.choices:
                column_data = getattr(obj,'get_%s_display'%column_name)()
            else:
                column_data = getattr(obj,column_name)
            td_ele = "<td>%s</td>"%column_data
            if index == 0:
                td_ele = "<td><a href='%s/change/'>%s</a></td>"%(obj.id,column_data)
            ele += td_ele
        # else:
        #     ele += "<td><button class='label label-table label-info'>登录</button></td>"
    else:
        ele += "<td><a href='%s/change/'>%s</a></td>"%(obj.id,obj)
    return mark_safe(ele)

@register.simple_tag
def render_paginator(querysets,filter_conditions,sorted_column):
    """
    分页
    :param querysets:
    :return:
    """
    ele = """<ul class="pagination text-nowrap mar-no"><li class="page-pre disabled"><a href="#">&lt;</a></li>"""
    # page_range是所有的页，querysets.number是当前页
    if querysets:
        for i in querysets.paginator.page_range:
            if abs(querysets.number - i) < 3:
                active = ''
                if querysets.number == i:
                    active = 'active'
                filter_ele = render_filter_args(filter_conditions)
                sorted_ele = ''
                if sorted_column:
                    sorted_ele = "&_o=%s"%list(sorted_column.values())[0]
                p_ele = '''<li class="page-number"><a href="?page=%s%s%s">%s</a></li>'''%(str(i),str(filter_ele),sorted_ele,str(i))
                # p_ele = '''<li class="%s"><a href="?page=%s%s%s">%s</a></li>'''%(active,i,filter_ele,sorted_ele,i)
                ele += p_ele
    else:
        p_ele = '''<li class="page-number"><a href="?page=%s">%s</a></li>''' % (
        '1','1')
        # p_ele = '''<li class="%s"><a href="?page=%s%s%s">%s</a></li>'''%(active,i,filter_ele,sorted_ele,i)
        ele += p_ele
    ele += """<li class="page-next"><a href="#">&gt;</a></li></ul>"""
    return mark_safe(ele)

def render_filter_args(filter_conditions):
    if filter_conditions:
        print("filter_conditions",filter_conditions)
        ele = ''
        for k,v in filter_conditions.items():
            ele +='&%s=%s'%(k,v)
        return mark_safe(ele)
    else:
        return ''

@register.simple_tag()
def options(model,field):
    choices = []
    model = model._meta.model
    print("model:%s,field:%s" % (model._meta.model, field))
    if hasattr(model,"%s_set"%field):
        querysets = getattr(model,"%s_set"%field).rel.related_model.objects.all()
        print("querysets1:",querysets)
        for queryset in querysets:
            choices.append({queryset.id:queryset.model})
    elif hasattr(model,"%s_choices"%field):
        querysets = getattr(model,"%s_choices"%field)
        print("querysets2:", querysets)
        for queryset in querysets:
            choices.append({queryset[0]:queryset[1]})
    elif hasattr(model,field):
        querysets = getattr(model,field).get_queryset()
        print("querysets3:", querysets)
        # if hasattr(obj,'get_queryset'):
        #     querysets = getattr(obj,'get_queryset')()
        for queryset in querysets:
            choices.append({queryset.id:queryset.name})
    print("choices:",choices)
    return choices

@register.simple_tag
def get_current_sort_index(sorted_column):
    return list(sorted_column.values())[0] if sorted_column else ''

@register.simple_tag()
def get_selected_option(filter_condition,field,choice):
    # print("field:%s----choice:%s----filter_condition:%s"%(field,choice,filter_condition))
    value = filter_condition.get(field)
    if value:
        if value == str(choice):
            return 'selected'
    return

