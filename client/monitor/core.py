import hashlib,time
import requests
import sys

class ReportData(object):
    # 上报数据
    def __init__(self,url,timeout,token_id,username):
        self.url = url
        self.timeout = timeout
        self.token_id = token_id
        self.username = username

    def report(self,data,method="post"):
        if method == "get":
            try:
                response = requests.get(self.url,params=data,timeout=self.timeout)
            except Exception as e:
                sys.exit("\033[31;1m%s\033[0m" % e)
        else:
            try:
                response = requests.post(self.url,data=data,timeout=self.timeout)
            except Exception as e:
                sys.exit("\033[31;1m%s\033[0m" % e)
        return response

    @staticmethod
    def get_token(username, token_id):
        timestamp = int(time.time())
        md5_format_str = "%s\n%s\n%s" % (username, timestamp, token_id)
        obj = hashlib.md5()
        obj.update(md5_format_str.encode('utf8'))
        print("token format:[%s]" % md5_format_str)
        print("token :[%s]" % obj.hexdigest())
        return obj.hexdigest()[10:17], timestamp

    def __attact_token(self):
        token,timestamp = self.get_token(self.username,self.token_id)
        self.url = self.url + "?user=%s&timestamp=%s&token=%s"%(username,timestamp,token)