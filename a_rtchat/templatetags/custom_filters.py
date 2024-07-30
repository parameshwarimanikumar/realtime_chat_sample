# a_rtchat/templatetags/custom_filters.py

from django import template
import os

register = template.Library()

@register.filter
def has_extension(value, extension):
    """
    Returns True if the file URL has the given extension.
    """
    return value.lower().endswith(extension.lower())
