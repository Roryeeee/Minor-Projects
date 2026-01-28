from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Template filter to get a dictionary item by key."""
    if dictionary and key in dictionary:
        return dictionary.get(key)
    return None
