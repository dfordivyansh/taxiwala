from django import template

register = template.Library()

@register.filter(name='dictkey')  # <-- IMPORTANT: name must match template usage
def dictkey(value, arg):
    return value.get(arg)
