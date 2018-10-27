from kingadmin.admin_base import BaseKingAdmin
class AdminSite(object):
    def __init__(self):
        self.enable_admins = {}

    #两个参数，一个表名，一个自定义的admin类
    def register(self,model_class,admin_class=BaseKingAdmin):
        '''注册admin表'''

        # print('register',model_class,admin_class)
        #获取app名字
        app_name = model_class._meta.app_label
        #获取表名
        model_name = model_class._meta.model_name
        if not admin_class:
            admin_class = BaseKingAdmin()
        else:
            admin_class = admin_class()
        admin_class.model = model_class
        if app_name not in self.enable_admins:
            self.enable_admins[app_name] = {}
        self.enable_admins[app_name][model_name] = admin_class

#实例化，就可以调用register方法
site = AdminSite()