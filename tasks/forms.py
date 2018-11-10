from django import forms
from tasks import models
from cmdb import models as cmdbmodels

class TaskForm(forms.Form):
    name = forms.CharField(max_length=64,label="任务名称")
    status_choices = (
        (0, '待处理'),
        (1, "处理中"),
        (2, "成功"),
        (3, '失败')
    )
    status = forms.IntegerField(widget=forms.Select(choices=status_choices))
    task_type_choices = (
        (0, "shell"),
        (1, "perl"),
        (2, "python")
    )
    task_type = forms.IntegerField(widget=forms.Select(choices=task_type_choices))
    # result = models.TextField("任务执行返回的结果")
    is_template = forms.BooleanField(default=False)
    content = forms.Textarea()
    #hosts = forms.ModelMultipleChoiceField(queryset=cmdbmodels.Asset.objects.all())
    exec_type_choices = (
        ('0', '立即执行'),
        ('1', '定时执行')
    )
    exec_type = forms.IntegerField(widget=forms.Select(choices=exec_type_choices))
    execplan = forms.ModelChoiceField(queryset=models.ExecPlan.objects.all())
    start_time = forms.DateField(widget=forms.SelectDateWidget)
    end_time = forms.DateTimeField()

    def __init__(self):
        self.fields['hosts'] = cmdbmodels.Asset.objects.all()
        return super(TaskForm, self).__init__()
