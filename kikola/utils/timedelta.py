"""
======================
kikola.utils.timedelta
======================

Useful functions to work with timedelta instances.

Contents
========

str_to_timedelta
----------------

Converts string to timedelta instance if possible.

timedelta_average
-----------------

Returns average timedelta from timedelta lists.

timedelta_div
-------------

Division one timedelta to another and return result as float number.

timedelta_seconds
-----------------

Return full number of seconds from timedelta instance.

timedelta_to_str
----------------

Converts timedelta instance to string using string formatters "G", "H", "i",
"s" or special formats "F", "f".

"""

import datetime
import re

from django.core.serializers.json import DjangoJSONEncoder
from django.template.defaultfilters import pluralize

from kikola.utils.digits import force_int


__all__ = ('TimedeltaJSONEncoder', 'str_to_timedelta', 'timedelta_average',
           'timedelta_div', 'timedelta_seconds', 'timedelta_to_str')


TIMEDELTA_FORMATS = {
    'G': '%(hours)d',
    'H': '%(hours)02d',
    'i': '%(minutes)02d',
    's': '%(seconds)02d',
}

timedelta_re = \
    re.compile(r'(?P<hours>\d+):(?P<minutes>\d+)(:(?P<seconds>\d+))?')


class TimedeltaJSONEncoder(DjangoJSONEncoder):
    """
    JSON encoder subclass that knows how to work with date/times, timedelta and
    decimal objects.
    """
    TIMEDELTA_FORMAT = 'G:i'

    def default(self, value):
        if isinstance(value, datetime.timedelta):
            return timedelta_to_str(value, self.TIMEDELTA_FORMAT)
        return super(TimedeltaJSONEncoder, self).default(value)


def str_to_timedelta(value):
    """
    Convert string value to timedelta instance if possible.
    """
    matched = timedelta_re.match(value)

    if matched:
        data = dict([(key, force_int(value, default=0)) \
                     for key, value in matched.groupdict().items()])

        return datetime.timedelta(hours=data['hours'],
                                  minutes=data['minutes'],
                                  seconds=data['seconds'])

    return None


def timedelta_average(*values):
    """
    Computes the arithmetic mean of list of timedeltas.
    """
    if isinstance(values[0], (list, tuple)):
        values = values[0]
    return sum(values, datetime.timedelta()) / len(values)


def timedelta_div(first, second):
    """
    By default, Python does not support timedeltas division and this
    function add ability to divide ``first`` timedelta by ``second`` timedelta.
    """
    first_seconds = timedelta_seconds(first)
    second_seconds = timedelta_seconds(second)

    if not second_seconds:
        return None

    return float(first_seconds) / float(second_seconds)


def timedelta_seconds(value):
    """
    Return full number of seconds from timedelta.

    By default, Python returns only one day seconds, not all timedelta seconds.
    """
    seconds = value.seconds

    if value.days:
        seconds += value.days * 24 * 60 * 60

    return seconds


def timedelta_to_str(value, format=None):
    """
    Display the timedelta, formatted according to the given string. If format
    string not set - using default "G:i" format.

    Use the same format as Django built-in ``{% now %}`` template tag, but
    support only "G", "H", "i" and "s" format strings.

    Also, you can use one specific format, "F" or "f". This would format
    timedelta "433:28" as "2 weeks, 4 days, 1:28:00" or "2w 4d 1:28:00".
    """
    if not isinstance(value, datetime.timedelta):
        return u''

    data = {
        'days': value.days,
        'hours': value.days * 24 + value.seconds / 3600,
        'minutes': value.seconds / 60 - value.seconds / 3600 * 60,
        'seconds': value.seconds % 60,
        'weeks': value.days / 7,
    }

    old_format = format or u'G:i'
    format = u''

    if not old_format in ('F', 'f'):
        for part in old_format:
            if part in TIMEDELTA_FORMATS.keys():
                part = TIMEDELTA_FORMATS[part]
            format += part
    else:
        if data['weeks']:
            format += '%(weeks)d%(weeks_label)s '

            data['days'] -= data['weeks'] * 7
            data['hours'] -= data['weeks'] * 7 * 24

            if old_format == 'f':
                data['weeks_label'] = 'w'
            else:
                data['weeks_label'] = ' week' + pluralize(data['weeks']) + ','

        if data['days']:
            format += '%(days)d%(days_label)s '

            data['hours'] -= data['days'] * 24

            if old_format == 'f':
                data['days_label'] = 'd'
            else:
                data['days_label'] = ' day' + pluralize(data['days']) + ','

        format += '%(hours)d:%(minutes)02d:%(seconds)02d'

    return format % data
