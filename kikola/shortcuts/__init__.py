"""
================
kikola.shortcuts
================

Useful shortcut functions for your Django projects.
"""

from django.conf import settings


__all__ = ('conf', )


def conf(name, default=None):
    """
    Shortcut to fast getting settings var.

    If settings ``name`` does not exist and ``default`` value is ``None``,
    ``AttributeError`` would be raised.
    """
    if default is not None:
        return getattr(settings, name, default)
    return getattr(settings, name)
