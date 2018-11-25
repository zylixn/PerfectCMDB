from django.db import models

# Create your models here.
class Alarm(models.Model):
    name = models.CharField(max_length=64,unique=True)
    count = models.SmallIntegerField(default=1)
    memo = models.TextField(u'备注', null=True, blank=True)
    tag = models.ForeignKey('Tag',on_delete=models.CASCADE)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name_plural = u'告警表'
        unique_together = ('name',)

    def __str__(self):
        return self.name

class Service(models.Model):
    status_choices = (
        ('0','正常'),
        ('1','异常')
    )
    name = models.CharField(max_length=64,unique=True)
    status = models.SmallIntegerField(default=0)

    class Meta:
        verbose_name_plural = u'服务表'

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=64,unique=True)
    create_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = u'标签表'

    def __str__(self):
        return self.name