"""
Custom model fields for Django.
"""

import datetime
import re

from django import VERSION
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils import simplejson
from django.utils.encoding import smart_str
from django.utils.translation import ugettext_lazy as _

from kikola import forms
from kikola.shortcuts import conf
from kikola.utils import str_to_timedelta, timedelta_seconds

if conf('USE_CPICKLE', False):
    import cPickle as pickle
else:
    import pickle

# Try to add custom fields to ``south`` app
try:
    from south.modelsinspector import add_introspection_rules
except ImportError:
    add_introspection_rules = lambda *args, **kwargs: None


__all__ = ('JSONField', 'MonthField', 'PickleField', 'TimeDeltaField',
           'URLField')


class JSONField(models.TextField):
    """
    Model field that stores all Python object as JSON string.

    You should set custom encoder class for dumps Python object to JSON data
    via ``encoder_cls`` keyword argument. By default, ``DjangoJSONEncoder``
    would be used.
    """
    __metaclass__ = models.SubfieldBase

    encoder_cls = None

    def __init__(self, *args, **kwargs):
        self.encoder_cls = kwargs.pop('encoder_cls', DjangoJSONEncoder)
        super(JSONField, self).__init__(*args, **kwargs)

    def contribute_to_class(self, cls, name):
        super(JSONField, self).contribute_to_class(cls, name)

        def get_json(model):
            return self.get_db_prep_value(getattr(model, self.attname))
        setattr(cls, 'get_%s_json' % self.name, get_json)

        def set_json(model, json):
            setattr(model, self.attname, self.to_python(json))
        setattr(cls, 'set_%s_json' % self.name, set_json)

    def formfield(self, **kwargs):
        defaults = {'form_class': forms.JSONField}
        defaults.update(kwargs)
        field = super(JSONField, self).formfield(**defaults)

        if hasattr(field.widget, 'json_options') and \
           not 'cls' in field.widget.json_options:
            field.widget.json_options.update({'cls': self.encoder_cls})

        return field

    def get_default(self):
        if self.has_default():
            if callable(self.default):
                return self.default()
            return self.default
        return super(JSONField, self).get_default()

    def get_prep_value(self, value):
        return simplejson.dumps(value, cls=self.encoder_cls)

    def to_python(self, value):
        if not isinstance(value, basestring):
            return value

        if value == '':
            return value

        try:
            return simplejson.loads(value, encoding=conf('DEFAULT_CHARSET'))
        except ValueError, e:
            # If string could not parse as JSON it's means that it's Python
            # string saved to JSONField.
            return value


class MonthField(models.DateField):
    """
    Field to store month values.

    Originally, field store date with first day of the month.
    """
    __metaclass__ = models.SubfieldBase

    description = _('Month')

    def get_prep_value(self, value):
        if not value:
            return value

        return value - datetime.timedelta(days=value.day - 1)

    def to_python(self, value):
        if not value:
            return value

        return value - datetime.timedelta(days=value.day - 1)


class PickleField(models.TextField):
    """
    Custom field that enables to store pickled Python objects.
    """
    __metaclass__ = models.SubfieldBase

    editable = False
    serialize = False

    def get_default(self):
        if self.has_default():
            if callable(self.default):
                return self.default()
            return self.default
        return super(PickleField, self).get_default()

    def get_prep_value(self, value):
        return pickle.dumps(value)

    def to_python(self, value):
        if not isinstance(value, basestring):
            return value

        try:
            return pickle.loads(smart_str(value))
        except (EOFError, IndexError, KeyError, ValueError):
            # If pickle could not loads from string it's means that it's Python
            # string saved to PickleField.
            return value


class TimeDeltaField(models.IntegerField):
    """
    Polished version of ``TimeDeltaField`` from
    http://www.djangosnippets.org/snippets/1060/

    The field stores Python's datetime.timedelta in an integer column.
    """
    __metaclass__ = models.SubfieldBase

    default_error_messages = {
        'invalid': _('This value must be a timedelta.'),
    }
    description = _('Timedelta')

    def formfield(self, **kwargs):
        defaults = {'form_class': forms.TimeDeltaField}
        defaults.update(kwargs)
        return super(TimeDeltaField, self).formfield(**defaults)

    def get_prep_value(self, value):
        if value is None or isinstance(value, int):
            return value

        if isinstance(value, basestring):
            value = str_to_timedelta(value)

            if value is None:
                return self.null and None or 0

        assert isinstance(value, datetime.timedelta), (value, type(value))
        return timedelta_seconds(value)

    def to_python(self, value):
        if value is None or isinstance(value, datetime.timedelta):
            return value

        if isinstance(value, (int, long)):
            return datetime.timedelta(seconds=value)

        # Try to convert string time to timedelta instance
        if isinstance(value, basestring):
            new_value = str_to_timedelta(value)

            if new_value is not None:
                return new_value

        # If cannot convert value to timedelta raise ``AssertionError``
        assert False, (value, type(value))


class URLField(models.URLField):
    """
    Custom field that enables to store absolute URL, not only schemed value.
    """
    def formfield(self, **kwargs):
        defaults = {'form_class': forms.URLField,
                    'verify_exists': self.verify_exists}
        defaults.update(kwargs)
        return super(URLField, self).formfield(**defaults)


# Make able to store Django model objects in ``PickleField``
def picklefield(func):
    def wrapper(obj, field):
        if isinstance(field, PickleField):
            return field.get_db_prep_save(obj)
        return func(obj, field)
    return wrapper


models.Model.prepare_database_save = \
    picklefield(models.Model.prepare_database_save)


# Add south support
rules = [
    ((JSONField, ), [], {'encoder_cls': ['encoder_cls', {}]}),
    ((MonthField, ), [], {}),
    ((PickleField, ), [], {}),
    ((TimeDeltaField, ), [], {}),
    ((URLField, ), [], {}),
]

add_introspection_rules(rules, ['^kikola\.db\.fields'])


# Rename ``get_prep_value`` methods to ``get_db_prep_value`` for compatible
# with Django < 1.2
if VERSION[:2] < (1, 2):
    fields = (JSONField, MonthField, PickleField, TimeDeltaField, URLField)
    for field in fields:
        method = getattr(field, 'get_prep_value', None)
        if method is None:
            continue
        setattr(field, 'get_db_prep_value', method)
        delattr(field, 'get_prep_value')
