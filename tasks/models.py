from django.db import models
from django.utils import timezone
from cmdb import models as cmdb_models

class ExecPlan(models.Model):
    name = models.CharField(max_length=64)
    execplan = models.CharField(
        max_length=64,
        help_text="""
        0:5 0代表分钟，即每隔5分钟执行一次
        1:5 1代表小时，即每隔5小时执行一次
        2:5 2代表天，即每隔5天执行一次
        """
    )
    def __str__(self):
        return self.name

class Task(models.Model):
    name = models.CharField(max_length=64)
    status_choices = (
        (0,'待处理'),
        (1,"处理中"),
        (2,"成功"),
        (3,'失败')
    )
    status = models.SmallIntegerField(choices=status_choices,default='0')
    task_type_choices = (
        (0,"shell"),
        (1,"perl"),
        (2,"python")
    )
    task_type = models.SmallIntegerField(choices=task_type_choices,default='0')
    #result = models.TextField("任务执行返回的结果")
    is_template = models.BooleanField(default=False)
    content = models.TextField()
    hosts = models.ManyToManyField(cmdb_models.Asset,through="TaskHost")
    exec_type_choices = (
        (0,'立即执行'),
        (1,'定时执行')
    )
    exec_type = models.SmallIntegerField(choices=exec_type_choices,default='0')
    execplan = models.ForeignKey("ExecPlan",on_delete=models.PROTECT)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return self.name

class TaskLog(models.Model):
    task = models.ForeignKey("Task",on_delete=models.PROTECT)
    detail_log = models.TextField()

    def __str__(self):
        return str(self.id)

class TaskHost(models.Model):
    task = models.ForeignKey("Task",on_delete=models.PROTECT)
    host = models.ForeignKey(cmdb_models.Asset,on_delete=models.PROTECT)
    status_choices = (
        (0,"成功"),
        (1,"失败")
    )
    status = models.SmallIntegerField(choices=status_choices,default=0)
    create_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(self.id)

    class Meta:
        # auto_created = True
        db_table = "task_host_relationship"

class Template(models.Model):
    """
    原子能力
    """
    name = models.CharField(max_length=64)
    content = models.TextField()

    def __str__(self):
        return self.name
"""
class Busicomposer(models.Model):
    composerid = models.PositiveIntegerField()
    composername = models.CharField(max_length=64,null=False,blank=False)
    createuser = models.CharField(max_length=64)
    createtime = models.DateField(default=timezone.now)
    updatetime = models.DateTimeField(default=timezone.now)
    ispublished_choices = (
        (0,"N"),
        (1,"Y")
    )
    ispublished = models.SmallIntegerField(choices=ispublished_choices,default=0)
    publishuser = models.CharField(max_length=64)


    def __str__(self):
        return self.composername

    class Meta:
        db_table = "busicomposer"
"""


