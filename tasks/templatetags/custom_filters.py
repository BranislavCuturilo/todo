from django import template
from datetime import timedelta


register = template.Library()


@register.filter(name="multiply")
def multiply(value, factor):
    """Multiply two numbers in templates: {{ a|multiply:b }}"""
    try:
        return int(value) * int(factor)
    except (TypeError, ValueError):
        try:
            return float(value) * float(factor)
        except (TypeError, ValueError):
            return ""


@register.filter(name="get_item")
def get_item(mapping, key):
    """Get dict item by key in templates: {{ mydict|get_item:mykey }}"""
    if mapping is None:
        return None
    try:
        if hasattr(mapping, "get"):
            return mapping.get(key)
        return mapping[key]
    except Exception:
        return None


@register.filter(name="add_days")
def add_days(value, days):
    """Add days to a date: {{ date|add_days:7 }}"""
    try:
        if hasattr(value, 'date'):
            # If it's a datetime, get the date part
            date_value = value.date()
        else:
            date_value = value
        return date_value + timedelta(days=int(days))
    except (TypeError, ValueError):
        return value


@register.filter(name="split")
def split(value, delimiter):
    """Split a string by delimiter: {{ "a,b,c"|split:"," }}"""
    try:
        return value.split(delimiter)
    except (TypeError, AttributeError):
        return []


