from plugin import plugin_api
import platform
import sys

class InfoCollection(object):

    def get_platform(self):
        return platform.system()

    def collect(self):
        os_platform = self.get_platform()
        try:
            func = getattr(self,os_platform)
            info_data = func()
            return info_data
        except AttributeError as e:
            sys.exit("Error:MadKing doens't support os [%s]! " % os_platform)

    def Linux(self):
        sys_info = plugin_api.LinuxSysInfo()
        return sys_info

    def Windows(self):
        sys_info = plugin_api.WindowsSysInfo()
        return sys_info