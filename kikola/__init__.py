"""
======
kikola
======

Collection of Django's custom form fields and widgets, model field, reusabble
apps, middlewares, context processors and other useful utilities.
"""


__all__ = ('get_version', )


VERSION = (0, 5, 2)


def get_version(version=None):
    """
    Return kikola version number in human readable form.
    """
    version = version or VERSION
    if len(version) > 2 and version[2] is not None:
        if isinstance(version[2], int):
            return '%d.%d.%d' % version
        return '%d.%d-%s' % version
    return '%d.%d' % version[:2]
