"""
======================
kikola.utils.timedelta
======================

Useful functions to work with timedelta instances.

Contents
========

str_to_timedelta
----------------

Converts string to timedelta instance according to the given format.

If format not set function tries to load timedelta using default and magic
"full" formats.

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

Formats a timedelta according to the given format.

Use the same format as Django ``date`` template filter or PHP ``date``
function.

"""

import datetime
import re

from django.core.serializers.json import DjangoJSONEncoder
from django.template.defaultfilters import pluralize
from django.utils.translation import ugettext, ungettext

from kikola.shortcuts import conf
from kikola.utils.digits import force_int


__all__ = ('TimedeltaJSONEncoder', 'str_to_timedelta', 'timedelta_average',
           'timedelta_div', 'timedelta_seconds', 'timedelta_to_str')


SECONDS_PER_DAY = 86400
SECONDS_PER_WEEK = 604800
TIMEDELTA_FORMAT = conf('TIMEDELTA_FORMAT', 'G:i')
TIMEDELTA_FORMATS = {
    'd': (u'%(days)02d', r'(?P<days>\d{2,})'),
    'f': (u'%(weeks)d%(short_weeks_label)s ' \
          u'%(week_days)d%(short_week_days_label)s ' \
          u'%(day_hours)d:%(hour_minutes)02d:%(minute_seconds)02d',
          r'((?P<weeks>\d+)%(short_weeks_label)s )?' \
          r'((?P<week_days>\d{1,})%(short_week_days_label)s )?' \
          r'(?P<hours>\d{1,2})\:(?P<minutes>\d{2})(\:(?P<seconds>\d{2}))?'),
    'F': (u'%(weeks)d %(weeks_label)s, %(week_days)d %(week_days_label)s, ' \
          u'%(day_hours)d:%(hour_minutes)02d:%(minute_seconds)02d',
          r'((?P<weeks>\d+) %(weeks_label)s, )?' \
          r'((?P<week_days>\d{1,}) %(week_days_label)s, )?' \
          r'(?P<hours>\d{1,2})\:(?P<minutes>\d{2})(\:(?P<seconds>\d{2}))?'),
    'g': (u'%(day_hours)d', r'(?P<day_hours>\d{1,2})'),
    'G': (u'%(hours)d', r'(?P<hours>\d+)'),
    'h': (u'%(day_hours)02d', r'(?P<day_hours>\d{2})'),
    'H': (u'%(hours)02d', r'(?P<hours>\d{2,})'),
    'i': (u'%(hour_minutes)02d', r'(?P<hour_minutes>\d{2})'),
    'I': (u'%(minutes)02d', r'(?P<minutes>\d{2,})'),
    'j': (u'%(days)d', r'(?P<days>\d+)'),
    'l': (u'%(days_label)s', r'%(days_label)s'),
    'L': (u'%(weeks_label)s', r'%(weeks_label)s'),
    'm': (u'%(week_days_label)s', r'%(week_days_label)s'),
    'r': (u'%(days)d%(short_days_label)s ' \
          u'%(day_hours)d:%(hour_minutes)02d:%(minute_seconds)02d',
          r'((?P<days>\d+)%(short_days_label)s )?' \
          r'(?P<hours>\d{1,2})\:(?P<minutes>\d{2})\:(?P<seconds>\d{2})'),
    'R': (u'%(days)d %(days_label)s, ' \
          u'%(day_hours)d:%(hour_minutes)02d:%(minute_seconds)02d',
          r'((?P<days>\d+) %(days_label)s, )?' \
          r'(?P<hours>\d{1,2})\:(?P<minutes>\d{2})\:(?P<seconds>\d{2})'),
    's': (u'%(minute_seconds)02d', r'(?P<minute_seconds>\d{2})'),
    'S': (u'%(seconds)02d', r'(?P<seconds>{2,})'),
    'u': (u'%(microseconds)d', r'(?P<microseconds>\d{1,})'),
    'w': (u'%(week_days)d', r'(?P<week_days>\d{1})'),
    'W': (u'%(weeks)d', r'(?P<weeks>\d+)'),
}


class TimedeltaJSONEncoder(DjangoJSONEncoder):
    """
    JSON encoder subclass that knows how to work with date/times, timedelta and
    decimal objects.
    """
    TIMEDELTA_FORMAT = TIMEDELTA_FORMAT

    def default(self, value):
        if isinstance(value, datetime.timedelta):
            return timedelta_to_str(value, self.TIMEDELTA_FORMAT)
        return super(TimedeltaJSONEncoder, self).default(value)


def str_to_timedelta(value, format=None):
    """
    Convert string value to timedelta instance according to the given format.

    If format not set function tries to load timedelta using default
    ``TIMEDELTA_FORMAT`` and then both of magic "full" formats.

    You should also specify list of formats and function tries to convert
    to timedelta using each of formats in list. First matched format would
    return the converted timedelta instance.

    If user specified format, but function cannot convert string to
    new timedelta instance - ``ValueError`` would be raised. But if user did
    not specify the format, function would be fail silently and return ``None``
    as result.
    """
    def timedelta_kwargs(data):
        """
        Convert day_hours, hour_minutes, minute_seconds, week_days and weeks to
        timedelta seconds.
        """
        seconds = data.get('seconds', 0)
        seconds += data.get('day_hours', 0) * 3600
        seconds += data.pop('hour_minutes', 0) * 60
        seconds += data.pop('minute_seconds', 0)
        seconds += data.pop('week_days', 0) * SECONDS_PER_DAY
        seconds += data.pop('weeks', 0) * SECONDS_PER_WEEK
        data.update({'seconds': seconds})
        return data

    if not isinstance(value, basestring):
        raise ValueError('Only "basestring" instances supported by this ' \
                         'function. You use %s.' % type(value))

    user_format = format

    if isinstance(format, (list, tuple)):
        formats = tuple(format)
    elif format is None:
        formats = (TIMEDELTA_FORMAT, 'F', 'f')
    else:
        formats = (format, )

    locale_data = {
        'days_label': u'(%s|%s)' % (ugettext(u'day'), ugettext(u'days')),
        'short_days_label': ugettext(u'd'),
        'short_week_days_label': ugettext(u'd'),
        'short_weeks_label': ugettext(u'w'),
        'week_days_label': u'(%s|%s)' % (ugettext(u'day'), ugettext(u'days')),
        'weeks_label': u'(%s|%s)' % (ugettext(u'week'), ugettext(u'weeks')),
    }
    regexps = []

    for format in formats:
        processed = r'^'

        for part in format:
            if part in TIMEDELTA_FORMATS:
                part = TIMEDELTA_FORMATS[part][1] % locale_data
            else:
                part = re.escape(part)
            processed += part

        processed += r'$'
        regexps.append(processed)

    for regexp in regexps:
        timedelta_re = re.compile(regexp)
        matched = timedelta_re.match(value)

        if matched:
            data = dict([(key, force_int(value, 0)) \
                        for key, value in matched.groupdict().items()])
            return datetime.timedelta(**timedelta_kwargs(data))

    if user_format:
        raise ValueError('Cannot convert %r to timedelta instance, ' \
                         'using %r format.' % (value, user_format))

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
    return SECONDS_PER_DAY * value.days + value.seconds


def timedelta_to_str(value, format=None):
    """
    Display the timedelta formatted according to the given string.

    You should use global setting ``TIMEDELTA_FORMAT`` to specify default
    format to this function there (like ``DATE_FORMAT`` for builtin ``date``
    template filter).

    Default value for ``TIMEDELTA_FORMAT`` is ``'G:i'``.

    Format uses the same policy as Django ``date`` template filter or
    PHP ``date`` function with several differences.

    Available format strings:

    +------------------+-----------------------------+------------------------+
    | Format character | Description                 | Example output         |
    +==================+=============================+========================+
    | ``a``            | Not implemented.            |                        |
    +------------------+-----------------------------+------------------------+
    | ``A``            | Not implemented.            |                        |
    +------------------+-----------------------------+------------------------+
    | ``b``            | Not implemented.            |                        |
    +------------------+-----------------------------+------------------------+
    | ``B``            | Not implemented.            |                        |
    +------------------+-----------------------------+------------------------+
    | ``c``            | Not implemented.            |                        |
    +------------------+-----------------------------+------------------------+
    | ``d``            | Total days, 2 digits with   | ``'01'``, ``'41'``     |
    |                  | leading zeros. Do not       |                        |
    |                  | combine with ``w`` format.  |                        |
    +------------------+-----------------------------+------------------------+
    | ``D``            | Not implemented.            |                        |
    +------------------+-----------------------------+------------------------+
    | ``f``            | Magic "full" format with    | ``'2w 4d 1:28:07'``    |
    |                  | short labels.               |                        |
    +------------------+-----------------------------+------------------------+
    | ``F``            | Magic "full" format with    | ``'2 weeks, 4 days,    |
    |                  | normal labels.              | 1:28:07'``             |
    +------------------+-----------------------------+------------------------+
    | ``g``            | Day, not total, hours       | ``'0'`` to ``'23'``    |
    |                  | without leading zeros. To   |                        |
    |                  | use with ``d``, ``j``, or   |                        |
    |                  | ``w``.                      |                        |
    +------------------+-----------------------------+------------------------+
    | ``G``            | Total hours without         | ``'1'``, ``'433'``     |
    |                  | leading zeros. Do not       |                        |
    |                  | combine with ``g`` or       |                        |
    |                  | ``h`` formats.              |                        |
    +------------------+-----------------------------+------------------------+
    | ``h``            | Day, not total, hours with  | ``'00'`` to ``'23'``   |
    |                  | leading zeros. To use with  |                        |
    |                  | ``d`` or ``w``.             |                        |
    +------------------+-----------------------------+------------------------+
    | ``H``            | Total hours with leading    | ``'01', ``'433'``      |
    |                  | zeros. Do not combine with  |                        |
    |                  | ``g`` or ``h`` formats.     |                        |
    +------------------+-----------------------------+------------------------+
    | ``i``            | Hour, not total, minutes, 2 | ``00`` to ``'59'``     |
    |                  | digits with leading zeros   |                        |
    |                  | To use with ``g``, ``G``,   |                        |
    |                  | ``h`` or ``H`` formats.     |                        |
    +------------------+-----------------------------+------------------------+
    | ``I``            | Total minutes, 2 digits or  | ``'01'``, ``'433'``    |
    |                  | more with leading zeros. Do |                        |
    |                  | not combine with ``i``      |                        |
    |                  | format.                     |                        |
    +------------------+-----------------------------+------------------------+
    | ``j``            | Total days, one or 2 digits | ``'1'``, ``'41'``      |
    |                  | without leading zeros. Do   |                        |
    |                  | not combine with ``w``      |                        |
    |                  | format.                     |                        |
    +------------------+-----------------------------+------------------------+
    | ``J``            | Not implemented.            |                        |
    +------------------+-----------------------------+------------------------+
    | ``l``            | Days long label.            | ``'day'`` or           |
    |                  | Pluralized and localized.   | ``'days'``             |
    +------------------+-----------------------------+------------------------+
    | ``L``            | Weeks long label.           | ``'week'`` or          |
    |                  | Pluralized and localized.   | ``'weeks'``            |
    +------------------+-----------------------------+------------------------+
    | ``m``            | Week days long label.       | ``'day'`` or           |
    |                  | Pluralized and localized.   | ``'days'``             |
    +------------------+-----------------------------+------------------------+
    | ``M``            | Not implemented.            |                        |
    +------------------+-----------------------------+------------------------+
    | ``n``            | Not implemented.            |                        |
    +------------------+-----------------------------+------------------------+
    | ``N``            | Not implemented.            |                        |
    +------------------+-----------------------------+------------------------+
    | ``O``            | Not implemented.            |                        |
    +------------------+-----------------------------+------------------------+
    | ``P``            | Not implemented.            |                        |
    +------------------+-----------------------------+------------------------+
    | ``r``            | Standart Python timedelta   | ``'18 d 1:28:07'``     |
    |                  | representation with short   |                        |
    |                  | labels.                     |                        |
    +------------------+-----------------------------+------------------------+
    | ``R``            | Standart Python timedelta   | ``'18 days, 1:28:07'`` |
    |                  | representation with normal  |                        |
    |                  | labels.                     |                        |
    +------------------+-----------------------------+------------------------+
    | ``s``            | Minute, not total, seconds, | ``'00'`` to ``'59'``   |
    |                  | 2 digits with leading       |                        |
    |                  | zeros. To use with ``i`` or |                        |
    |                  | ``I``.                      |                        |
    +------------------+-----------------------------+------------------------+
    | ``S``            | Total seconds. 2 digits or  | ``'00'``, ``'433'``    |
    |                  | more with leading zeros. Do |                        |
    |                  | not combine with ``s``      |                        |
    |                  | format.                     |                        |
    +------------------+-----------------------------+------------------------+
    | ``t``            | Not implemented.            |                        |
    +------------------+-----------------------------+------------------------+
    | ``T``            | Not implemented.            |                        |
    +------------------+-----------------------------+------------------------+
    | ``u``            | Second, not total,          | ``0`` to ``999999``    |
    |                  | microseconds.               |                        |
    +------------------+-----------------------------+------------------------+
    | ``U``            | Not implemented.            |                        |
    +------------------+-----------------------------+------------------------+
    | ``w``            | Week, not total, days, one  | ``0`` to ``6``         |
    |                  | digit without leading       |                        |
    |                  | zeros. To use with ``W``.   |                        |
    +------------------+-----------------------------+------------------------+
    | ``W``            | Total weeks, one or more    | ``'1'``, ``'41'``      |
    |                  | digits without leading      |                        |
    |                  | zeros.                      |                        |
    +------------------+-----------------------------+------------------------+
    | ``y``            | Not implemented.            |                        |
    +------------------+-----------------------------+------------------------+
    | ``Y``            | Not implemented.            |                        |
    +------------------+-----------------------------+------------------------+
    | ``z``            | Not implemented.            |                        |
    +------------------+-----------------------------+------------------------+
    | ``Z``            | Not implemented.            |                        |
    +------------------+-----------------------------+------------------------+

    For example,

    ::

        >>> import datetime
        >>> from kikola.utils import timedelta_to_str
        >>> delta = datetime.timedelta(seconds=99660)
        >>> timedelta_to_str(delta)
        ... u'27:41'
        >>> timedelta_to_str(delta, 'r')
        ... u'1d 3:41:00'
        >>> timedelta_to_str(delta, 'f')
        ... u'1d 3:41'
        >>> timedelta_to_str(delta, 'W L, w l, H:i:s')
        ... u'0 weeks, 1 day, 03:41:00'

    Couple words about magic "full" formats. These formats show weeks number
    with week label, days number with day label and seconds only if weeks
    number, days number or seconds greater that zero.

    For example,

    ::

        >>> import datetime
        >>> from kikola.utils import timedelta_to_str
        >>> delta = datetime.timedelta(hours=12)
        >>> timedelta_to_str(delta, 'f')
        ... u'12:00'
        >>> timedelta_to_str(delta, 'F')
        ... u'12:00'
        >>> delta = datetime.timedelta(hours=12, seconds=30)
        >>> timedelta_to_str(delta, 'f')
        ... u'12:00:30'
        >>> timedelta_to_str(delta, 'F')
        ... u'12:00:30'
        >>> delta = datetime.timedelta(hours=168)
        >>> timedelta_to_str(delta, 'f')
        ... u'2w 0:00'
        >>> timedelta_to_str(delta, 'F')
        ... u'2 weeks, 0:00'

    """
    # Only ``datetime.timedelta`` instances allowed for this function
    if not isinstance(value, datetime.timedelta):
        raise ValueError('Only "datetime.timedelta" instances supported ' \
                         'by this function. You use %s.' % type(value))

    # Generate total data
    days = value.days
    microseconds = value.microseconds
    seconds = timedelta_seconds(value)

    hours = seconds / 3600
    minutes = seconds / 60
    weeks = days / 7

    # Generate collapsed data
    day_hours = hours - days * 24
    hour_minutes = minutes - hours * 60
    minute_seconds = seconds - minutes * 60
    week_days = days - weeks * 7

    days_label = ungettext(u'day', u'days', days)
    short_days_label = ugettext(u'd')
    short_week_days_label = ugettext(u'd')
    short_weeks_label = ugettext(u'w')
    week_days_label = ungettext(u'day', u'days', week_days)
    weeks_label = ungettext(u'week', u'weeks', weeks)

    # Collect data
    data = locals()

    format = format or TIMEDELTA_FORMAT
    processed = u''

    for part in format:
        if part in TIMEDELTA_FORMATS:
            is_full_part = part in ('f', 'F')
            is_repr_part = part in ('r', 'R')

            part = TIMEDELTA_FORMATS[part][0]

            if is_full_part or is_repr_part:
                if is_repr_part and not days:
                    part = part.replace(u'%(days)d', u'')
                    part = part.replace(u'%(days_label)s,', u'')
                    part = part.replace(u'%(short_days_label)s', u'')

                if is_full_part and not minute_seconds:
                    part = part.replace(u':%(minute_seconds)02d', u'')

                if is_full_part and not weeks:
                    part = part.replace(u'%(weeks)d', u'')
                    part = part.replace(u'%(short_weeks_label)s', u'')
                    part = part.replace(u'%(weeks_label)s,', u'')

                if is_full_part and not week_days:
                    part = part.replace(u'%(week_days)d', u'')
                    part = part.replace(u'%(short_week_days_label)s', u'')
                    part = part.replace(u'%(week_days_label)s,', u'')

                part = part.strip()
                part = u' '.join(part.split())

        processed += part

    return processed % data
