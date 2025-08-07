from django import template

register = template.Library()

@register.filter
def mul(value, arg):
    """
    Multiplies the value by the argument.
    Usage: {{ value|mul:5 }}
    """
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def div(value, arg):
    """
    Divides the value by the argument.
    Usage: {{ value|div:5 }}
    """
    try:
        if float(arg) == 0:
            return 0
        return float(value) / float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def percentage(value, total):
    """
    Calculates percentage of value from total.
    Usage: {{ value|percentage:total }}
    """
    try:
        if float(total) == 0:
            return 0
        return round((float(value) / float(total)) * 100, 1)
    except (ValueError, TypeError):
        return 0

@register.filter
def format_duration(minutes):
    """
    Formats minutes into hours and minutes.
    Usage: {{ minutes|format_duration }}
    """
    try:
        minutes = int(minutes)
        if minutes < 60:
            return f"{minutes} min"
        hours = minutes // 60
        remaining_minutes = minutes % 60
        if remaining_minutes == 0:
            return f"{hours}h"
        return f"{hours}h {remaining_minutes}min"
    except (ValueError, TypeError):
        return "0 min"

@register.filter 
def days_between(date1, date2):
    """
    Calculates days between two dates.
    Usage: {{ date1|days_between:date2 }}
    """
    try:
        delta = date2 - date1
        return delta.days
    except (AttributeError, TypeError):
        return 0