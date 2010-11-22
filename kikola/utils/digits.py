"""
===================
kikola.utils.digits
===================

Helpers to simplify work with integer or float numbers.

Contents
========

force_int
---------

Fail silently function to convert any Python object to ``int`` if possible. If
not returns ``None`` as well.

"""

import re

from django.utils.encoding import smart_str


__all__= ('force_int', )


integer_re = re.compile('(\d+)')


def force_int(value, default=None):
    """
    Convert any Python object to ``int``.

    Very useful function to get integer values from GET or POST requests and
    prevent corrupted data.
    """
    try:
        return int(value)
    except (TypeError, ValueError):
        matched = integer_re.match(smart_str(value).strip())
        if matched:
            return force_int(matched.group())
        return default
