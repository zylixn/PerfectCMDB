import os,sys
import yaml
import json

BASEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(BASEDIR)
sys.path.append(BASEDIR)
from core import ReportData
from plugin.linux import cpu
from plugin.linux import memory


if __name__ == '__main__':
    data = dict()
    yamlpath = os.path.join(BASEDIR,"conf.yaml")
    fh = open(yamlpath,'r',encoding='utf8')
    config = yaml.load(fh.read())
    print(config)
    timeout = config['timeout']
    url = "http://" + str(config['server']) + ":" + str(config['port']) + str(config['api'])
    print(url)
    token_id = config['token_id']
    username = config['username']
    obj = ReportData(url,timeout,token_id,username)
    cpuinfo = cpu.getcpuinfo()
    data['cpuinfo'] = cpuinfo
    memoryinfo = memory.getmemoryinfo()
    data['memoryinfo'] = memoryinfo
    response = obj.report({'asset_data':json.dumps(data)})