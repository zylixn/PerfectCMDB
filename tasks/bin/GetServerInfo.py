"""
采集服务器信息脚本
"""
import json
import psutil
from subprocess import Popen

#获取CPU信息
def getcpuinfo():
    result = dict()
    cpu_nums = psutil.cpu_count() # CPU全部个数
    logical_nums = psutil.cpu_count(logical=False) # CPU物理核心数量
    cpu_info = psutil.cpu_times() # 获取cpu的用户 / 系统 / 空闲时间：
    cpu_per = psutil.cpu_percent()
    result['cpu_nums'] = cpu_nums
    result['logical_num'] = logical_nums
    result['cpu_per'] = cpu_per
    result['cpu_info'] = cpu_info
    return result

# 获取内存信息
def getmemoryinfo():
    result = dict()
    virtual_memory = psutil.virtual_memory()
    result['total'] = virtual_memory.total
    result['available'] = virtual_memory.available
    result['used'] = virtual_memory.used
    result['percent'] = virtual_memory.percent
    result['free'] = virtual_memory.free
    return result

# 获取网络信息
def getnetworkinfo():
    result = dict()
    networkinfo = psutil.net_io_counters()
    result['bytes_sent'] = networkinfo.bytes_sent
    result['bytes_recv'] = networkinfo.bytes_recv
    result['packets_sent'] = networkinfo.packets_sent
    result['packets_recv'] = networkinfo.packets_recv
    return result


if __name__ == '__main__':
    getcpuinfo()