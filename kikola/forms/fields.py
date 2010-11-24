"""
===================
kikola.forms.fields
===================

Custom form fields for Django.
"""

from django import forms
from django.forms import ValidationError
from django.test import Client

from kikola.forms.widgets import JSONWidget, TimeDeltaWidget
from kikola.utils import str_to_timedelta, timedelta_seconds


__all__ = ('JSONField', 'TimeDeltaField', 'URLField')


class JSONField(forms.CharField):

    widget = JSONWidget


class TimeDeltaField(forms.IntegerField):

    widget = TimeDeltaWidget

    def clean(self, value):
        # Convert string time to timedelta instance and then convert to
        # seconds value
        if isinstance(value, basestring):
            value = str_to_timedelta(value)

            if value:
                value = timedelta_seconds(value)

        return super(TimeDeltaField, self).clean(value)


class URLField(forms.URLField):
    """
    Adds validation absolute pathes, like ``/some/path`` to Django's URLField.
    """
    def clean(self, value):
        if value.startswith('/'):
            if self.verify_exists:
                client = Client()
                try:
                    response = client.get(value)
                    if response.status_code != 200:
                        raise Exception
                except:
                    raise ValidationError(self.error_messages['invalid_link'])
            return value

        return super(URLField, self).clean(value)
