import psutil

def getcpuinfo():
    cpuinfo = dict()
    # cpu逻辑数量
    cpuinfo['cpucount'] = psutil.cpu_count()
    # cpu物理核心
    cpuinfo['logicalcount'] = psutil.cpu_count(logical=True)
    cpuinfo['percpu'] = psutil.cpu_percent(interval=1,percpu=True)
    return cpuinfo

if __name__ == '__main__':
    cpuinfo = getcpuinfo()
    print(cpuinfo)



