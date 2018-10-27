from django.contrib import admin
from cmdb.models import ServerInfor,Credential,Menu

class ServerInforAdmin(admin.ModelAdmin):
    model = ServerInfor
    list_display = ('ip','name','hostname','createdatetime')

class CredentialAdmin(admin.ModelAdmin):
    model = Credential
    list_display = ('name','port','username','password')

class MenuAdmin(admin.ModelAdmin):
    model = Menu
    list_display = ('name','url_type','url_name','url_alias')

admin.site.register(Menu,MenuAdmin)
admin.site.register(ServerInfor,ServerInforAdmin)
admin.site.register(Credential,CredentialAdmin)