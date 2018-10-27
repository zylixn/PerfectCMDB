import json
from django.shortcuts import render
class BaseKingAdmin(object):
    list_display = []
    list_filter = []
    search_fields = []
    # 只读
    readonly_fields = []
    filter_horizontal = []
    list_per_page = 5
    default_actions = []
    actions = []

    def delete_selected_objs(self,request,querysets):
        querysets_id = json.dumps([i.id for i in querysets])
        return render(request,'kingadmin/table_obj_delete.html',{'admin_class':self,
                                                                 'objs':querysets,
                                                                 'querysets_ids':querysets_id})