__author = "liyl"
import os
BaseDir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

Params = {
    "server": "127.0.0.1",
    "port":5000,
    'request_timeout':30,
    "urls":{
          "asset_report_with_no_id":"/cmdb/asset/report/",
          "asset_report":"/cmdb/asset/report/",
        },
    'asset_id': '%s/var/.asset_id' % BaseDir,
    'log_file': '%s/logs/run_log' % BaseDir,

    'auth':{
        'user':'lili0219@126.com',
        'token': 'abc'
        },
}

if __name__ == '__main__':
    print(BaseDir)