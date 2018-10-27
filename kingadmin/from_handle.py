#-*-coding:utf-8-*-
#!/usr/bin/env python
from django.forms import ModelForm

def create_dynamic_model_form(admin_class,form_add=False):
    """
    动态生成modelform
    :param admin_class:
    :return:
    """
    class Meta:
        model = admin_class.model
        fields = "__all__"
        if not form_add: # change
            exclude = admin_class.readonly_fields
            admin_class.form_add = False
        else:
            admin_class.form_add = True

    def __new__(cls,*args,**kwargs):
        for field_name in cls.base_fields:
            field_obj = cls.base_fields[field_name]
            field_obj.widget.attrs.update({'class':'form-control'})
        return ModelForm.__new__(cls)
    dynamic_form = type('DynamicModelForm',(ModelForm,),{"Meta":Meta,"__new__":__new__})
    return dynamic_form