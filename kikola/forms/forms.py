"""
Custom forms for Django.
"""

import base64
import hashlib
import pickle
import re
from random import choice, randint

from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from widgets import CaptchaWidget, CaptchaTokenWidget, SpanWidget


__all__ = ('CaptchaForm', 'TabbedForm')

class CaptchaForm(forms.Form):
    """
    Simple mathematical captcha form. It generates captcha example with two
    digits that added or multiplicated.
    """
    captcha = forms.CharField(max_length=2, help_text=_('Are you human?'),
        widget=CaptchaWidget(attrs={'size': 10, 'class': 'captcha'}))
    captcha_token = forms.CharField(widget=CaptchaTokenWidget)

    def __init__(self, *args, **kwargs):
        super(CaptchaForm, self).__init__(*args, **kwargs)
        token = self.data.get('captcha_token', None)
        self.generate_captcha(token)

    def check_captcha(self, token, answer):
        answer = int(answer)
        captcha = self._decode(token)

        if answer != eval(captcha):
            raise ValueError('Captcha answer is not right for this expression.')

        return True

    def clean_captcha_token(self):
        answer = self.cleaned_data.get('captcha')
        token = self.cleaned_data.get('captcha_token')

        if not answer:
            return token

        try:
            self.check_captcha(token, answer)
        except ValueError, e:
            self.generate_captcha()
            self.fields['captcha'].widget.render_value = False

            e = forms.ValidationError(_('Please, calculate expression and ' \
                                        'type right answer.'))
            self._errors['captcha'] = e.messages

        return token

    def generate_captcha(self, token=None):
        if token:
            captcha = self._decode(token)
        else:
            captcha = '%d%s%d' % (randint(1, 9), choice('+*'), randint(1, 9))
            token = self._encode(captcha)

        self.fields['captcha'].label = mark_safe(
            u'<span class="number-%d">&#%d</span>&#%d' \
             '<span class="number-%d">&#%d</span>=' % (randint(0, 99),
                                                       ord(captcha[0]),
                                                       ord(captcha[1]),
                                                       randint(0, 99),
                                                       ord(captcha[2])))
        self.fields['captcha_token'].widget.value = token

    def _decode(self, token):
        key, data = token[:40], token[40:]
        captcha = pickle.loads(base64.standard_b64decode(data))

        if key != self._secret_key(captcha):
            raise ValueError, 'Secret key was broken.'

        return captcha

    def _encode(self, captcha):
        key = self._secret_key(captcha)
        data = base64.standard_b64encode(pickle.dumps(captcha))
        return key + data

    def _secret_key(self, captcha):
        key = hashlib.sha1(settings.SECRET_KEY + captcha).hexdigest()
        return key

class TabbedForm(forms.Form):
    """
    Class added auto-incremented ``tabindex`` attribute to all non-hidden form
    field.
    """
    def __init__(self, *args, **kwargs):
        super(TabbedForm, self).__init__(*args, **kwargs)
        self.auto_tabindex()

    def auto_tabindex(self, start=0):
        setattr(self, '_tabindex', start)

        for field in self:
            widget = field.field.widget

            if not isinstance(widget, (SpanWidget, forms.HiddenInput)):
                self._tabindex += 1
                widget.attrs['tabindex'] = self._tabindex

    # Leave ``tabindex`` method for compatible
    def tabindex(self, start=0):
        if not hasattr(self, '_tabindex'):
            setattr(self, '_tabindex', start)
        setattr(self, '_tabindex', getattr(self, '_tabindex') + 1)
        return getattr(self, '_tabindex')
