from django.shortcuts import render,HttpResponse,redirect
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from tasks.models import Task,Template,TaskHost,TaskLog,ExecPlan
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from tasks.admin import TaskAdmin, TemplateAdmin
from cmdb.models import Asset
from django.utils import timezone
from tasks import forms as tasks_forms
from cmdb import utils
import traceback
from tasks import tasks
from celery import group

def test(request):
    print("It's a test start")
    s = tasks.add.apply_async((2,2), queue="test_add")
    result = s.get()
    # result = tasks.getserverinfo()
    print("It's a test end")
    return HttpResponse("%s"%result)

class TaskCreate(CreateView):
    form_class = tasks_forms.TaskForm
    template_name = "tasks/task_create.html"
    success_url = "/tasks/list/"

    def form_invalid(self, form):
        return super(TaskCreate, self).form_invalid()
    
    def get(self, request, *args, **kwargs):
        form_obj = tasks_forms.TaskForm()
        return render(request,self.template_name,{'form':form_obj})
    
    def post(self, request, *args, **kwargs):
        task = dict()
        form_obj = tasks_forms.TaskForm(request.POST)
        if form_obj.is_valid():
            task = form_obj.cleaned_data
            hosts = task['hosts']
            del task['hosts']
            obj = Task(**task)
            obj.save()
            obj.hosts.add(*hosts)
            obj.save()
            return redirect('/tasks/list/')
        return redirect('/tasks/create/')

class TaskList(ListView):
    model = Task
    template_name = 'tasks/task_list.html'
    # permission_required = 'cmdb.can_view_serverinfo'
    raise_exception = True

    def get_context_data(self, *, object_list=None, **kwargs):
        filter_conditions = {}
        sorted_column = None
        context = super(TaskList, self).get_context_data(**kwargs)
        querysets = Task.objects.get_queryset().order_by('id')
        try:
            querysets = utils.search_by(self.request, querysets, TaskAdmin)
            querysets, filter_conditions = utils.get_filter_result(self.request, querysets)
            querysets, sorted_column = utils.get_orderby_result(self.request, querysets, TaskAdmin)
            paginator = Paginator(querysets, TaskAdmin.list_per_page)
            page = self.request.GET.get('page')
            try:
                querysets = paginator.page(page)
            except PageNotAnInteger:
                querysets = paginator.page(1)
            except EmptyPage:
                querysets = paginator.page(paginator.num_pages)
        except Exception as e:
            traceback.print_exc()

        # AssetAdmin.filter_conditions = filter_conditions
        context['tasks'] = querysets
        context['sorted_column'] = sorted_column
        context['model'] = Task
        context['list_filter'] = TaskAdmin.list_filter
        context['list_display'] = TaskAdmin.list_display
        context['search_fields'] = TaskAdmin.search_fields
        context['filter_conditions'] = filter_conditions
        # print("model:%s,admin_class:%s"%(type(Asset),type(AssetAdmin)))
        return context

    def post(self,request):
        IDS = request.POST.get('IDS')
        print("IDS:",IDS)
        arr = IDS.split('-')
        if arr:
            Asset.objects.filter(id__in=arr).delete()
        return redirect('/cmdb/servers/')

class TaskDetail(DetailView,CreateView):
    model = Task
    form_class = tasks_forms.TaskForm
    template_name = 'tasks/task_detail.html'

    def get_context_data(self, **kwargs):
        context = super(TaskDetail, self).get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context

    def get(self, request, *args, **kwargs):
        # print(self.queryset)
        form_obj = tasks_forms.TaskForm(instance=self.get_object())
        return render(request,self.template_name,{'form':form_obj})

class TemplatesList(ListView):
    model = Template
    template_name = 'tasks/template_list.html'
    # permission_required = 'cmdb.can_view_serverinfo'
    raise_exception = True

    def get_context_data(self, *, object_list=None, **kwargs):
        filter_conditions = {}
        sorted_column = None
        context = super(TemplatesList, self).get_context_data(**kwargs)
        querysets = Template.objects.get_queryset().order_by('id')
        try:
            querysets = utils.search_by(self.request, querysets, TemplateAdmin)
            querysets, filter_conditions = utils.get_filter_result(self.request, querysets)
            querysets, sorted_column = utils.get_orderby_result(self.request, querysets, TemplateAdmin)
            paginator = Paginator(querysets, TemplateAdmin.list_per_page)
            page = self.request.GET.get('page')
            try:
                querysets = paginator.page(page)
            except PageNotAnInteger:
                querysets = paginator.page(1)
            except EmptyPage:
                querysets = paginator.page(paginator.num_pages)
        except Exception as e:
            traceback.print_exc()
        context['list_display1'] = []
        context['tasks'] = querysets
        context['sorted_column'] = sorted_column
        context['model'] = Template
        context['list_filter'] = TemplateAdmin.list_filter
        for field in TemplateAdmin.list_display:
            context['list_display1'].append(Template._meta.get_field(field).verbose_name)
        context['list_display'] = TemplateAdmin.list_display
        context['search_fields'] = TemplateAdmin.search_fields
        context['filter_conditions'] = filter_conditions
        print("list_display:",context['list_display'])
        return context

    def post(self,request):
        error = {}
        name = request.POST.get('name')
        content = request.POST.get('content')
        template = Template.objects.filter(name=name)
        IDS = request.POST.get('IDS')
        if not name and not IDS:
            return HttpResponse("输入的信息错误，请重新输入")
        elif IDS:
            arr = IDS.split('-')
            if arr:
                Template.objects.filter(id__in=arr).delete()
                return redirect("/tasks/templates/")
        if not template:
            obj = Template.objects.create(name=name,content=content)
            obj.save()
        else:
            error['error'] = "名字为{name}的模板已存在".format(name=name)
        print("*" * 10)
        return redirect("/tasks/templates/")



