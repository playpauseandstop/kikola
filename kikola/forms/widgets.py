"""
Custom forms widgets for Django.
"""

import datetime
import re

from time import strptime

from django import forms
from django.core.urlresolvers import NoReverseMatch, reverse
from django.core.serializers.json import DjangoJSONEncoder
from django.forms.util import flatatt
from django.utils import simplejson
from django.utils.dates import MONTHS, MONTHS_3
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe

from kikola.utils import timedelta_to_str


__all__ = ('AutocompleteWidget', 'JSONWidget', 'SelectDateWidget',
           'TimeDeltaWidget')


class AutocompleteWidget(forms.TextInput):
    """
    Autocomplete widget to use with jquery-autocomplete plugin.

    Widget can use for static and dynamic (AJAX-liked) data. Also
    you can relate some fields and it's values'll posted to autocomplete
    view.

    Widget support all jquery-autocomplete options that dumped to JavaScript
    via django.utils.simplejson.

    **Note** You must init one of ``choices`` or ``choices_url`` attribute.
    Else widget raises TypeError when rendering.
    """
    def __init__(self, attrs=None, choices=None, choices_url=None, options=None,
                 parent_widget=None, related_fields=None):
        """
        Optional arguments
        ------------------

            * ``choices`` - Static autocomplete choices (similar to choices
            used in Select widget).

            * ``choices_url`` - Path to autocomplete view or autocomplete
            url name.

            * ``options`` - jQuery autocomplete plugin options. Auto dumped
            to JavaScript via SimpleJSON

            * ``related_fields`` - Fields that relates to current (value
            of this field will sended to autocomplete view via POST)
        """
        self.attrs = attrs or {}
        self.choice, self.choices, self.choices_url = None, choices, choices_url
        self.options = options or {}
        self.parent_widget = parent_widget

        if related_fields:
            extra = {}
            if isinstance(related_fields, str):
                related_fields = list(related_fields)

            for field in related_fields:
                extra[field] = "%s_value" % field

            self.extra = extra
        else:
            self.extra = {}

    def render(self, name, value=None, attrs=None):
        if not self.choices and not self.choices_url:
            raise TypeError, \
                  'One of "choices" or "choices_url" keyword argument must ' \
                  'be supplied obligatory.'

        if self.choices and self.choices_url:
            raise TypeError, \
                  'Only one of "choices" or "choices_url" keyword argument ' \
                  'can be supplied.'

        choices = ''

        if self.choices:
            self.set_current_choice(value)
            choices = simplejson.dumps([unicode(v) for k, v in self.choices],
                                       ensure_ascii=False)
            html_code = HiddenInput().render(name, value=value)
            name += '_autocomplete'
        else:
            html_code = ''

        if self.choices_url:
            try:
                choices = simplejson.dumps(reverse(str(self.choices_url)))
            except NoReverseMatch:
                choices = simplejson.dumps(self.choices_url)

        if self.options or self.extra:
            if 'extraParams' in self.options:
                self.options['extraParams'].update(self.extra)
            else:
                self.options['extraParams'] = self.extra

            options = ', ' + simplejson.dumps(self.options,
                                              indent=4,
                                              sort_keys=True)
            extra = []

            for k, v in self.extra.items():
                options = options.replace(simplejson.dumps(v), v)
                extra.append(
                    u"function %s() { return $('#id_%s').val(); }\n" % (v, k)
                )

            extra = u''.join(extra)
        else:
            extra, options = '', ''

        final_attrs = self.build_attrs(attrs)

        if self.parent_widget is None:
            html_code += super(AutocompleteWidget, self).\
                         render(name, self.choice or value, attrs)
        else:
            html_code += self.parent_widget().\
                         render(name, self.choice or value, final_attrs)

        html_code += u"""
<script type="text/javascript"><!--
    %s$('#%s').autocomplete(%s%s);
--></script>
""" % (extra, final_attrs['id'], choices, options)

        return mark_safe(html_code)

    def set_current_choice(self, data):
        if not self.choices:
            raise ValueError('"choices" attribute was not defined yet.')

        for k, v in self.choices:
            if k == data:
                self.choice = v
                break

    def value_from_datadict(self, data, files, name):
        if not self.choices:
            return super(AutocompleteWidget, self).\
                   value_from_datadict(data, files, name)

        autocomplete_name = name + '_autocomplete'

        if not autocomplete_name in data:
            self.set_current_choice(data[name])
            return data[name]

        for k, v in self.choices:
            if v == data[autocomplete_name]:
                self.set_current_choice(k)
                return k


class JSONWidget(forms.Textarea):
    """
    Prettify dumps of all non-string JSON data, when string JSON data dumps
    without quotes.
    """
    def __init__(self, *args, **kwargs):
        self.json_options = kwargs.pop('json_options', {})
        super(JSONWidget, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None):
        if not isinstance(value, basestring):
            defaults = {'cls': DjangoJSONEncoder,
                        'ensure_ascii': False,
                        'indent': 4,
                        'sort_keys': True}
            defaults.update(self.json_options)
            value = simplejson.dumps(value, **defaults)

        return super(JSONWidget, self).render(name, value, attrs)


class SelectDateWidget(forms.Widget):
    """
    Extended version of django.newforms.extras.SelectDateWidget

    The main advantages are:

        * Widget can splits date input into custom <select> boxes.

        * Custom <select> boxes can have first empty <option>.
    """
    day_field = '%s_day'
    month_field = '%s_month'
    year_field = '%s_year'

    PATTERNS = (
        ('%b', 'month'),
        ('%B', 'month'),
        ('%d', 'day'),
        ('%m', 'month'),
        ('%y', 'year'),
        ('%Y', 'year'),
    )

    def __init__(self, *args, **kwargs):
        """
        Optional arguments
        ------------------

            * ``format_separator`` - separator in input_format. By default: -

            * ``input_format`` - valid date input format. By default:
              %B-%d-%Y

            * ``null`` - adds first empty <option> to all selects. By default:
              False

            * ``null_label`` - adds first empty <option> with this label to all
              selects. By default: ""

            * ``years`` - list/tuple of years to use in the "year" select box.
              By default: this year and next 9 printed.
        """
        self.attrs = kwargs.get('attrs', {})
        self.format_separator = kwargs.get('format_separator', '-')
        self.input_format = kwargs.get('input_format', '%B-%d-%Y')
        self.null = kwargs.get('null', False)
        self.null_label = kwargs.get('null_label', '')

        if 'years' in kwargs:
            self.years = kwargs['years']
        else:
            year = datetime.date.today().year
            self.years = range(year, year+10)

        fields = []
        parts = self.input_format.split(self.format_separator)

        for part in parts:
            for k, v in self.PATTERNS:
                if part == k:
                    fields.append((k, v))

        if not fields:
            raise TypeError('Date input format "%s" is broken.' % \
                            self.input_format)

        self.fields = fields
        self.input_format = \
            self.input_format.replace('%b', '%m').replace('%B', '%m')

    def render(self, name, value, attrs=None):
        try:
            year, month, day = value.year, value.month, value.day
        except AttributeError:
            year = month = day = None

            if isinstance(value, basestring):
                try:
                    t = strptime(value, self.input_format)
                    year, month, day = t[0], t[1], t[2]
                except:
                    pass

        def _choices(pattern):
            if pattern == '%b':
                choices = MONTHS_3.items()
                choices.sort()
            elif pattern == '%B':
                choices = MONTHS.items()
                choices.sort()
            elif pattern == '%d':
                choices = [(i, i) for i in range(1, 32)]
            elif pattern == '%m':
                choices = [(i, i) for i in range(1, 13)]
            elif pattern == '%y':
                choices = [(i, str(i)[-2:]) for i in self.years]
            elif pattern == '%Y':
                choices = [(i, i) for i in self.years]

            if self.null and not self.null_label:
                self.null_label = mark_safe('&mdash;')
            if self.null_label:
                choices.insert(0, (None, self.null_label))

            return tuple(choices)

        id_ = self.attrs.get('id', 'id_%s' % name)
        output = []

        for i, field in enumerate(self.fields):
            pattern, field_name = field
            field = getattr(self, '%s_field' % field_name)

            sel_name = field % name
            sel_value = locals().get(field_name, None)

            if i == 0:
                local_attrs = self.build_attrs(id=id_)
            else:
                local_attrs['id'] = field % id_

            sel = forms.Select(choices=_choices(pattern)).\
                        render(sel_name, sel_value, local_attrs)
            output.append(sel)

        return mark_safe('\n'.join(output))

    def value_from_datadict(self, data, files, name):
        value = []

        for pattern, field_name in self.fields:
            field = getattr(self, '%s_field' % field_name)
            field_value = data.get(field % name, None)
            if field_value and field_value != 'None':
                value.append(str(field_value))

        if value:
            return '-'.join(value)

        return data.get(name, None)


class TimeDeltaWidget(forms.TextInput):
    """
    Custom widget to use with ``kikola.forms.TimeDeltaField`` field class.
    """
    def render(self, name, value, attrs=None):
        if isinstance(value, int):
            value = timedelta_to_str(datetime.timedelta(seconds=value))
        elif isinstance(value, datetime.timedelta):
            value = timedelta_to_str(value)
        return super(TimeDeltaWidget, self).render(name, value, attrs)
