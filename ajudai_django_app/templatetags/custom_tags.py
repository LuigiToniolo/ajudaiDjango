from django import template

register = template.Library()

@register.filter 
def dict_key(d, k):
    '''Returns the given key from a dictionary.'''
    value = d.get(k)
    if(value):
        return d.get(k)
    return d.get('default')
