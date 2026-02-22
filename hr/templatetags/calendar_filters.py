from django import template

register = template.Library()

@register.filter(name='get_item')
def get_item(dictionary, key):
    """Получить элемент из словаря по ключу"""
    if dictionary is None:
        return None
    return dictionary.get(key)
