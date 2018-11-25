from django.contrib import admin
from tasks import models

class TaskAdmin(admin.ModelAdmin):
    list_display = ('id','name','task_type','status')
    list_filter = ('task_type','status')
    list_per_page = 5
    search_fields = ('name',)


class ExecPlanAdmin(admin.ModelAdmin):
    list_display = ('name','execplan')

class TemplateAdmin(admin.ModelAdmin):
    list_display = ('name','content')

admin.site.register(models.ExecPlan,ExecPlanAdmin)
admin.site.register(models.Task,TaskAdmin)
admin.site.register(models.Template,TemplateAdmin)
admin.site.register(models.TaskHost)

