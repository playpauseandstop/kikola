"""
Custom model fields for Django.
"""
from django.conf import settings
from django.db import models
from django.utils import simplejson

from kikola.forms import fields
from kikola.forms.widgets import JSONWidget


__all__ = ('JSONField', 'PickleField', 'URLField')


if getattr(settings, 'USE_CPICKLE', False):
    import cPickle as pickle
else:
    import pickle


class JSONField(models.TextField):
    """
    Model field that stores all Python object as JSON string.
    """
    __metaclass__ = models.SubfieldBase

    def contribute_to_class(self, cls, name):
        super(JSONField, self).contribute_to_class(cls, name)

        def get_json(model):
            return self.get_db_prep_value(getattr(model, self.attname))
        setattr(cls, 'get_%s_json' % self.name, get_json)

        def set_json(model, json):
            setattr(model, self.attname, self.to_python(json))
        setattr(cls, 'set_%s_json' % self.name, set_json)

    def formfield(self, **kwargs):
        kwargs['widget'] = JSONWidget(attrs={'class': 'vLargeTextField'})
        return super(JSONField, self).formfield(**kwargs)

    def get_db_prep_value(self, value):
        return simplejson.dumps(value)

    def to_python(self, value):
        if not isinstance(value, basestring):
            return value

        if value == '':
            return value

        try:
            return simplejson.loads(value, encoding=settings.DEFAULT_CHARSET)
        except ValueError, e:
            # If string could not parse as JSON it's means that it's Python
            # string saved to JSONField.
            return value


class PickleField(models.TextField):
    """
    Custom field that enables to store pickled Python objects.
    """
    __metaclass__ = models.SubfieldBase

    editable = False
    serialize = False

    def get_db_prep_value(self, value):
        return pickle.dumps(value)

    def get_default(self):
        if self.has_default():
            if callable(self.default):
                return self.default()
            return self.default
        return super(PickleField, self).get_default()

    def to_python(self, value):
        if not isinstance(value, basestring):
            return value

        try:
            return pickle.loads(smart_str(value))
        except (EOFError, IndexError, KeyError, ValueError):
            # If pickle could not loads from string it's means that it's Python
            # string saved to PickleField.
            return value


class URLField(models.URLField):
    """
    Custom field that enables to store absolute URL, not only schemed value.
    """
    def formfield(self, **kwargs):
        defaults = {'form_class': fields.URLField,
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
