"""
Custom form fields for Django.
"""

from django.forms import URLField as BaseURLField
from django.forms import ValidationError
from django.test import Client


__all__ = ('URLField',)

class URLField(BaseURLField):
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
