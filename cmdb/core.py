from django.core.exceptions import ObjectDoesNotExist
from cmdb import models
import json

class AssetHandler(object):
    def __init__(self,request):
        self.req = request
        self.required_fields = ['asset_id','sn','asset_type']
        self.response = {
            'error':[],
            'info':[],
            'warning':[],
        }

    def response_msg(self,msg_type,key,val):
        if msg_type in self.response:
            self.response[msg_type].append({key:val})
        else:
            raise ValueError

    def __check_data(self,data,only_check_sn=False):
        for field in data:
            if field not in data:
                self.response_msg('error','RequiredChecked','The field %s required'%field)

        else:
            if self.response['error']:return False

        try:
            if only_check_sn:
                self.asset_obj = models.Asset.objects.get(sn=data['sn'])
            else:
                self.asset_obj = models.Asset.objects.get(id=data['asset_id'],sn=data['sn'])
        except ObjectDoesNotExist:
            self.response_msg('error','AssetInvalid','cannot find Asset id=%s and sn= %s in DataBase'%(data['asset_id'],data['sn']))
            self.wait_approval = True
            return False

    def handler_asset(self):
        """
        判断资产是不是新增，如果含有asset_id，则将信息插入到相应的信息表里面，否则这入到带审批区
        :return:
        """
        pass
