from django import forms
from tasks import models
from cmdb import models as cmdbmodels
from django.forms.fields import DateField,DateTimeField

# class TaskForm(forms.Form):
#     name = forms.CharField(max_length=64,label="任务名称",widget=forms.Textarea(attrs={}))
#     status_choices = (
#         (0, '待处理'),
#         (1, "处理中"),
#         (2, "成功"),
#         (3, '失败')
#     )
#     status = forms.IntegerField(widget=forms.Select(choices=status_choices))
#     task_type_choices = (
#         (0, "shell"),
#         (1, "perl"),
#         (2, "python")
#     )
#     task_type = forms.IntegerField(widget=forms.Select(choices=task_type_choices))
#     # result = models.TextField("任务执行返回的结果")
#     is_template = forms.BooleanField()
#     content = forms.Textarea()
#     hosts = forms.ModelMultipleChoiceField(queryset=cmdbmodels.Asset.objects.all())
#     exec_type_choices = (
#         ('0', '立即执行'),
#         ('1', '定时执行')
#     )
#     exec_type = forms.IntegerField(widget=forms.Select(choices=exec_type_choices))
#     execplan = forms.ModelChoiceField(queryset=models.ExecPlan.objects.all())
#     start_time = forms.DateField(widget=forms.SelectDateWidget)
#     end_time = forms.DateTimeField()

    # def __init__(self):
    #     self.fields['hosts'].queryset = cmdbmodels.Asset.objects.all()
    #     self.fields['execplan'].choices = models.ExecPlan.objects.all()
    #     super(TaskForm, self).__init__()

class TaskForm(forms.ModelForm):
    class Meta:
        model = models.Task
        fields = "__all__"

    def __new__(cls, *args, **kwargs):
        assets = cmdbmodels.Asset.objects.all()
        plans = models.ExecPlan.objects.all()
        cls.base_fields['hosts'] = forms.ModelMultipleChoiceField(queryset=assets)
        cls.base_fields['execplan'] = forms.ModelChoiceField(queryset=plans)
        for field_name in cls.base_fields:
            field_obj = cls.base_fields[field_name]
            field_obj.widget.attrs.update({'class': 'form-control input-sm'})
        return forms.ModelForm.__new__(cls)
