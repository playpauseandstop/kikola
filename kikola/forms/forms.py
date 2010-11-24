"""
==================
kikola.forms.forms
==================

Custom forms for Django.
"""

from django import forms


__all__ = ('TabbedForm', )


class TabbedForm(forms.Form):
    """
    Class added auto-incremented ``tabindex`` attribute to all non-hidden form
    field.
    """
    def __init__(self, *args, **kwargs):
        super(TabbedForm, self).__init__(*args, **kwargs)
        self.auto_tabindex()

    def auto_tabindex(self, start=0):
        self._tabindex = start

        for field in self:
            widget = field.field.widget

            if not isinstance(widget, forms.HiddenInput):
                self._tabindex += 1
                widget.attrs['tabindex'] = self._tabindex
