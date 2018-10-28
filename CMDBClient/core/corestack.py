__author__ = "lixn"
from conf import settings
from core import info_collection,api_token
import requests
import logging
import logging.handlers
import datetime
import sys
import os
import json

class ArgvHandler(object):
    def __init__(self,argvlist):
        self.argvlist = argvlist
        self.logger = logging.getLogger("mylogger")
        self.parse_argv()

    def parse_argv(self):
        if len(self.argvlist) > 1:
            if hasattr(self,self.argvlist[1]):
                func = getattr(self,self.argvlist[1])
                func()
            else:
                self.help_msg()
        else:
            self.help_msg()

    def load_assert_id(self):
        assert_id = None
        assert_file = settings.Params['asset_id']
        if os.path.isfile(assert_file):
            with open(assert_file) as f:
                assert_id = f.read()
            if assert_id.isdigit():
                return assert_id
            else:
                return None
        else:
            return None

    def __attach_token(self,url_str):
        '''generate md5 by token_id and username,and attach it on the url request'''
        user = settings.Params['auth']['user']
        token_id = settings.Params['auth']['token']

        md5_token,timestamp = api_token.get_token(user,token_id)
        url_arg_str = "user=%s&timestamp=%s&token=%s" %(user,timestamp,md5_token)
        if "?" in url_str:#already has arg
            new_url = url_str + "&" + url_arg_str
        else:
            new_url = url_str + "?" + url_arg_str
        return  new_url
        #print(url_arg_str)

    def report_asset(self):
        obj = info_collection.InfoCollection()
        asset_data = obj.collect()
        asset_id = self.load_assert_id()
        if asset_id:
            asset_data["asset_id"] = asset_id
            post_url = "asset_report"
        else:
            asset_data["asset_id"] = None
            post_url = "asset_report_with_no_id"
        data = {"asset_data":json.dumps(asset_data)}
        response = self.__submit_data(post_url,data,method="post")
        res_info = json.loads(response.text)
        if "asset_id" in res_info:
            self.__update_asset_id(res_info['asset_id'])

        self.log_record(res_info)


    def __submit_data(self,url_key=None,data=None,method="get"):
        if url_key in settings.Params['urls']:
            url = "http://%s:%s%s"%(settings.Params['server'],settings.Params['port'],settings.Params['urls'][url_key])
        else:
            url = "http://%s:%s%s"%(settings.Params['server'],settings.Params['urls'][url_key])
        url = self.__attach_token(url)
        if method == "get":
            try:
                response = requests.get(url,params=data,timeout=settings.Params['request_timeout'])
            except Exception as e:
                sys.exit("\033[31;1m%s\033[0m" % e)
        else:
            try:
                response = requests.post(url,data=data,timeout=settings.Params['request_timeout'])
            except Exception as e:
                sys.exit("\033[31;1m%s\033[0m" % e)
        # callback = json.loads(response)
        return response

    def __update_asset_id(self,new_asset_id):
        asset_id_file = settings.Params["asset_id"]
        with open(asset_id_file,"wb") as f:
            f.write(str(new_asset_id))

    def run_forever(self):
        pass

    def help_msg(self):
        msg = '''
        collect_data       收集硬件信息
        run_forever
        get_asset_id
        report_asset       收集硬件信息并汇报 
        '''
        print(msg)

    def log_record(self,msg):
        log_file = settings.Params['log_file']
        self.logger.setLevel(logging.DEBUG)
        rf_handler = logging.handlers.TimedRotatingFileHandler(log_file,when='midnight', interval=1, \
                                                       backupCount=7, atTime=datetime.time(0, 0, 0, 0))
        rf_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

        self.logger.addHandler(rf_handler)
        self.logger.info(msg)
