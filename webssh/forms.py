# coding=utf-8
from django import forms
# from django.forms import ModelForm
from webssh.models import Host, SshUser
from django.forms.widgets import CheckboxSelectMultiple

# from django.contrib.auth.models import User, Group


class HostForm(forms.ModelForm):
    # 前端主机添加页面

    class Meta:
        model = Host
        fields = '__all__'
        # exclude = ("asset_type",)

        widgets = {
            'user': CheckboxSelectMultiple,
            'usergroup': CheckboxSelectMultiple,
        }

        # error_messages = {
        #     'model':{
        #         'max_length': ('太短了'),
        #     }
        # }

        # help_texts = {
        #     'user': u'哪些登陆用户能对当前主机进行操作，超级用户直接有操作权限'
        # }

    # model_field = Meta.model._meta.get_field('user')
    # user = forms.ModelMultipleChoiceField(widget=CheckboxSelectMultiple, queryset=User.objects.filter(is_superuser=False), label=model_field.verbose_name, required=False, help_text=model_field.help_text)


class HostForm2(HostForm):
    # 前端主机编辑页面去除 主机类型 字段

    class Meta(HostForm.Meta):
        exclude = ('asset_type', )


class SshUserForm(forms.ModelForm):
    # password = forms.CharFie()ld(label=u"密码", widget=forms.PasswordInput, required=False)

    class Meta:
        model = SshUser
        fields = '__all__'
        # exclude = ("id",)

        widgets = {
            'password': forms.PasswordInput(),
        }

        labels = {

        }

        help_texts = {
        }
        error_messages = {

        }

