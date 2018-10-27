from django import template
from django.utils.safestring import mark_safe
from django.db.models import Q
from cmdb import models

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