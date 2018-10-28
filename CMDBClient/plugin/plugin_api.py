from plugin.linux import sysinfo

def LinuxSysInfo():
    #print __file__
    return  sysinfo.collect()


def WindowsSysInfo():
    from plugin.windows import sysinfo as win_sysinfo
    return win_sysinfo.collect()