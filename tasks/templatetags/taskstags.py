from django import template

register = template.Library()

@register.simple_tag()
def get_field(form,field):
    # print(dir(form))
    # print("=================field:%s========"%field)
    if hasattr(form,field):
        m = getattr(form,field)
        return m
    else:
        return