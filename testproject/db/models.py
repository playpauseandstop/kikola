import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _

from kikola.db.fields import JSONField, MonthField, PickleField, TimeDeltaField


__all__ = ('DummyObject', 'JSONModel', 'MonthModel', 'PickleModel',
           'TimeDeltaModel')


TODAY = datetime.date.today


class DummyObject(object):
    """
    Dummy object for storing in pickle field.
    """
    def __eq__(self, other):
        return type(self) == type(other)


class JSONModel(models.Model):
    """
    Dummy model for testing ``JSONField`` fields.
    """
    bool_field = JSONField(_('bool field'), blank=True, default=True)
    dict_field = JSONField(_('dict field'), blank=True, default={})
    float_field = JSONField(_('float field'), blank=True, default=0.0)
    int_field = JSONField(_('int field'), blank=True, default=0)
    list_field = JSONField(_('list field'), blank=True, default=[])
    none_field = JSONField(_('None field'), blank=True, default=None)
    str_field = JSONField(_('string field'), blank=True, default='')
    unicode_field = JSONField(_('unicode field'), blank=True, default=u'')


class MonthModel(models.Model):
    """
    Dummy model for testing ``MonthModel`` fields.
    """
    default_month = MonthField(_('default month'), default=TODAY)
    first_month = MonthField(_('first month'))
    last_month = MonthField(_('last month'), blank=True, null=True)


class PickleModel(models.Model):
    """
    Dummy model for testing ``PickleField`` fields.
    """
    bool_field = PickleField(_('bool field'), blank=True, default=True)
    dict_field = PickleField(_('dict field'), blank=True, default={})
    float_field = PickleField(_('float field'), blank=True, default=0.0)
    int_field = PickleField(_('int field'), blank=True, default=0)
    list_field = PickleField(_('list field'), blank=True, default=[])
    long_field = PickleField(_('long field'), blank=True, default=0L)
    none_field = PickleField(_('None field'), blank=True, default=None)
    object_field = PickleField(_('object field'), blank=True,
        default=DummyObject())
    str_field = PickleField(_('string field'), blank=True, default='')
    tuple_field = PickleField(_('tuple field'), blank=True, default=tuple())
    unicode_field = PickleField(_('unicode field'), blank=True, default=u'')


class TimeDeltaModel(models.Model):
    """
    Dummy model for testing ``TimeDeltaField`` fields.
    """
    total_time = TimeDeltaField()
    average_total_time = TimeDeltaField(blank=True, null=True)
