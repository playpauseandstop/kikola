"""
==================================
kikola.templatetags.timedelta_tags
==================================

Shortcut to use ``timedelta_to_str`` function in Django templates as
``timedelta`` template filter.

Installation
============

Just add ``kikola`` to ``INSTALLED_APPS`` var of your project settings.

Contents
========

timedelta
---------

Represent ``datetime.timedelta`` instances in templates using
``kikola.utils.timedelta_to_str`` function.

Usage
~~~~~

Template code::

    {% load timedelta_tags %}
    "{{ delta|timedelta }}", "{{ delta|timedelta:"H:i:s" }}"
    "{{ not_delta|timedelta }}"

And context::

    delta = datetime.timedelta(hours=7, minutes=35, seconds=5)
    not_delta = 'string'

Gives next result::

    "7:35", "07:35:05"
    ""

"""

from django.template import Library

from kikola.utils.timedelta import timedelta_to_str


register = Library()


@register.filter
def timedelta(value, format=None):
    try:
        return timedelta_to_str(value, format)
    except ValueError:
        return u''
