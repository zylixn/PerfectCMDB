import psutil

def getmemoryinfo():
    memoryinfo = dict()
    memory = psutil.virtual_memory()
    memoryinfo['free'] = memory.free
    memoryinfo['total'] = memory.total
    memoryinfo['used'] = memory.used
    memoryinfo['percent'] = memory.percent
    return memoryinfo


if __name__ == '__main__':
    memory = getmemoryinfo()
    print(memory)