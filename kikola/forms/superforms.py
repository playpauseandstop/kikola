"""
SuperForm: a form that can contain sub-forms or a list of them.

Copyright (c) 2007, Jeroen van Dongen (jeroen<at>jkwadraat.net)
Copyright (c) 2008, Igor Davydenko (igor<at>wemakesites.org)
All rights reserved. Licensed under the same license as Django.

Known bugs
----------
 - Nesting a FormList of SuperForm's does not work as expected yet.
   At least the rendering is screwed up, however given the error
   pattern I suspect a more serious flaw.

Introduction
------------
Often you need part of a form multiple times. Either in the same form or
in different forms. SuperForm allows you to compose forms by using
forms in almost the same way you use fields. The resulting form
behaves just like any other Form, so you can even nest SuperForms
in SuperForms. And mix SuperForms and regular Forms. Also, you can
mix SubForms and regular Fields in a single SuperForm (just take note
of the field ordering, see below).

See the doctests below for examples.

Requirements
------------
SuperForm requires Django 1.0 Alpha version or higher.

Field naming
------------
If you include a Form in a SuperForm, with a name of 'postal_address',
the subform gets 'postal_address' as a prefix. When rendered, the
fields of the subform are named like 'postal_address-<name_of_field>'.

Accessing the cleaned_data can be done like:
    form.cleaned_data['postal_address']['name_of_field']

Errors can be accessed in the same way:
    form.errors['postal_address']['name_of_field']

Field ordering during rendering
-------------------------------
SubForms are rendered in the order they're defined.
If the SuperForm has fields of its own (instead of just subforms),
those will be rendered together BEFORE any of the subforms,
in the order they're defined.
If you don't want that to happen, layout your forms manually.

Doc tests
---------

>>> from django import forms
>>> class AddressForm(forms.Form):
...     street = forms.CharField()
...     city = forms.CharField()
>>> class BusinessLocationForm(SuperForm):
...     phone_num = forms.CharField()
...     visiting_address = SubForm(AddressForm)
...     postal_address = SubForm(AddressForm, required=False)
>>> f = BusinessLocationForm()
>>> f.is_bound
False
>>> f.as_table()
u'<tr><th><label for="id_phone_num">Phone num:</label></th><td><input type="text" name="phone_num" id="id_phone_num" /></td></tr>\\n<tr><th><label for="id_visiting_address-street">Street:</label></th><td><input type="text" name="visiting_address-street" id="id_visiting_address-street" /></td></tr>\\n<tr><th><label for="id_visiting_address-city">City:</label></th><td><input type="text" name="visiting_address-city" id="id_visiting_address-city" /></td></tr>\\n<tr><th><label for="id_postal_address-street">Street:</label></th><td><input type="text" name="postal_address-street" id="id_postal_address-street" /></td></tr>\\n<tr><th><label for="id_postal_address-city">City:</label></th><td><input type="text" name="postal_address-city" id="id_postal_address-city" /></td></tr>'
>>> data = {
...     'phone_num': '010 2207061',
...     'visiting_address-street': 'visiting street',
...     'visiting_address-city': 'visiting city',
...     'postal_address-street': 'postal street',
...     'postal_address-city': 'postal city',
... }
>>> f = BusinessLocationForm(data=data)
>>> f.is_valid()
True
>>> f.cleaned_data['phone_num']
u'010 2207061'
>>> f.cleaned_data['visiting_address']['street']
u'visiting street'
>>> f.cleaned_data['postal_address']['street']
u'postal street'
>>> del data['postal_address-street']
>>> f = BusinessLocationForm(data=data)
>>> f.is_valid()
False
>>> f.cleaned_data['visiting_address']['street']
Traceback (most recent call last):
    ...
AttributeError: cleaned_data
>>> f.errors['postal_address']['street']
[u'This field is required.']
>>> del data['postal_address-city']
>>> f = BusinessLocationForm(data=data)
>>> f.is_valid()
True
>>> f.cleaned_data['phone_num']
u'010 2207061'
>>> f.cleaned_data['visiting_address']['street']
u'visiting street'
>>> f.cleaned_data['postal_address']['street']
Traceback (most recent call last):
    ...
KeyError: 'postal_address'
"""

import copy
from django.forms.fields import Field
from django.forms.forms import Form
from django.forms.widgets import Media
from django.forms.util import ErrorDict, ErrorList, ValidationError
from django.forms.util import StrAndUnicode
from django.utils.datastructures import SortedDict

__all__ = ('SuperForm', 'SubForm', 'FormList')
NON_FIELD_ERRORS = '__all__'

class SortedDictFromList(SortedDict):
    """
    A dictionary that keeps its keys in the order in which they're inserted.
    """
    # This is different than django.utils.datastructures.SortedDict, because
    # this takes a list/tuple as the argument to __init__().
    def __init__(self, data=None):
        data = data or []
        self.keyOrder = [d[0] for d in data]
        dict.__init__(self, dict(data))

class SubForm(object):
    # Tracks each time a SubForm instance is created. Used to retain order.
    creation_counter = 0

    def __init__(self, form_def, required=True, initial=None):
        self.form_def = form_def
        self.required=required
        self.initial = initial
        self._form = None
        self.creation_counter = SubForm.creation_counter
        SubForm.creation_counter += 1

    def ignore_errors(self):
        return not (self.required or self._got_data(self._form))

    def _got_data(self, form):
        """
        Determines if there's data submitted for this subform
        """
        for k in self.data.keys():
            if k.startswith(form.prefix):
                return True
        return False

    def is_valid(self):
        if self._form.is_valid():
            return True
        else:
            if self.ignore_errors():
                return True
            else:
                return False

    def init_form(self, prefix, auto_id="id_%s", initial=None,
                         data=None):
        if initial is None:
            initial = self.initial
        self._form = self.form_def(data=data, prefix=prefix, auto_id=auto_id,
                                   initial=initial)

    def __getattr__(self, name):
        return getattr(self._form, name)

    def __iter__(self):
        return self._form.__iter__()

class FormList(SubForm):
    def __init__(self, form_def, min_count=0, max_count=None,
                 initial_count=1, initial=None):
        self.min_count=min_count
        self.max_count=max_count
        self.initial_count = initial_count
        self._nf_errors = []
        self.__errors = None
        super(FormList, self).__init__(form_def=form_def,
                                       required=(min_count>0),
                                       initial=initial)

    def init_form(self, prefix, auto_id="id_%s", initial=None,
                  data=None):
        if initial is None:
            initial = self.initial
        if data is None:
            count = self.initial_count
        else:
            # figure out how many items there are in the datadict
            key = prefix
            count = 0
            for k in self.data.keys():
                if k.startswith(key):
                    count += 1
        self._forms = []
        self.prefix = prefix
        for i in range(0, count):
            f = self.form_def(data=data, prefix=prefix+"-%s" % i,
                              auto_id=auto_id, initial=initial)
            self._forms.append(f)

    def _errors(self):
        if self.__errors is None:
            error_dict = ErrorDict()
            for f in self._forms:
                error_dict[self._forms.index(f)] = f.errors
            if self._nf_errors:
                error_dict[NON_FIELD_ERRORS]=self._nf_errors
            self.__errors = error_dict
        return self.__errors
    errors = property(_errors)

    def _cleaned_data(self):
        if not hasattr(self, '__cleaned_data'):
            cleaned_data = []
            errors = False
            for f in self.forms:
                if hasattr(f, 'cleaned_data'):
                    cleaned_data.append(f.cleaned_data)
                else:
                    if isinstance(f, SubForm) and f.ignore_errors():
                        continue
                    else:
                        raise AttributeError, 'cleaned_data'
            self.__cleaned_data = cleaned_data
        return self.__cleaned_data
    cleaned_data = property(_cleaned_data)

    def is_valid(self):
        valid_count = 0
        for f in self._forms:
            if f.is_valid():
                valid_count += 1
                continue
            if self._got_data(f):
                return False
        if valid_count < self.min_count:
            # not enough items
            self._nf_errors.append(u'At least %s items are required' % \
                                   self.min_count)
            return False
        if valid_count > self.max_count:
            # too much items
            self._nf_errors.append(u'No more than %s items are allowed' % \
                                   self.max_count)
            return False
        return True

    def as_table(self):
        """
        Returns this form rendered as HTML <tr>s -- excluding the
        <table></table>.
        """
        subs = []
        for f in self._forms:
            subs.append(f.as_table())
        return "\n".join(subs)

class DeclarativeSubFormsMetaclass(type):
    """
    Metaclass that converts SubForm attributes to a dictionary called
    'base_subforms', taking into account parent class 'base_subforms' as well.
    """
    def __new__(cls, name, bases, attrs):
        subfields = [(fieldname, attrs.pop(fieldname)) \
                     for fieldname, obj in attrs.items() \
                     if isinstance(obj, Field)]
        subfields.sort(lambda x, y: cmp(x[1].creation_counter, \
                                        y[1].creation_counter))

        subforms = [(form_prefix, attrs.pop(form_prefix)) \
                    for form_prefix, obj in attrs.items() \
                    if isinstance(obj, SubForm)]
        subforms.sort(lambda x, y: cmp(x[1].creation_counter, \
                                       y[1].creation_counter))

        # NOTE: we don't support subclassing of SuperForms yet.
        # -----------------------------------------------------
        # If this class is subclassing another SuperForm, add that SuperForm's
        # subforms.
        # Note that we loop over the bases in *reverse*. This is necessary in
        # order to preserve the correct order of fields.
        #for base in bases[::-1]:
        #    if hasattr(base, 'base_fields'):
        #        fields = base.base_fields.items() + fields

        attrs['base_subfields'] = SortedDictFromList(subfields)
        attrs['base_subforms'] = SortedDictFromList(subforms)
        return type.__new__(cls, name, bases, attrs)

class BaseSuperForm(StrAndUnicode):
    def __init__(self, data=None, auto_id='id_%s', prefix=None, initial=None):
        self.is_bound = data is not None
        self.data = data
        self.auto_id = auto_id
        self.prefix = prefix
        self.initial = initial or {}
        self.__errors = None # Stores the errors after clean() has been called.

        # create a list of subform instances
        finst_list = []
        # if we've fields of our own, collect them first and put
        # 'm in a form of their own
        if len(self.base_subfields) > 0:
            self_form = Form(data=data, auto_id=auto_id,
                             prefix=self.prefix, initial=initial)
            self_form.fields = self.base_subfields.copy()
            finst_list.append( ("_self", self_form,) )

        # now do our subforms ...
        for (name, fd) in self.base_subforms.items():
            subform_prefix = self.add_prefix(name)
            fd.init_form(prefix=subform_prefix,
                         auto_id=auto_id,
                         initial=initial,
                         data=data)
            finst_list.append( (subform_prefix, fd,) )
        self.forms = SortedDictFromList(finst_list)

    def __unicode__(self):
        return self.as_table()

    def __iter__(self):
        for form in self.forms.values():
            for field in form:
                yield field

    def __getitem__(self, name):
        """
        Returns a BoundField with the given name.
        """
        try:
            return self.forms[name]
        except KeyError:
            return self.forms['_self'][name]

    def is_valid(self):
        """
        Returns True if all subforms are either valid or
        empty and not required. False otherwise.
        """
        # first check if we're bound ...
        if self.is_bound:
            # then check every subform ...
            for form in self.forms.values():
                if not form.is_valid():
                    return False
        else:
            return False
        return True

    def add_prefix(self, field_name):
        """
        Returns the field name with a prefix appended, if this Form has a
        prefix set.

        Subclasses may wish to override.
        """
        return self.prefix and \
               ('%s-%s' % (self.prefix, field_name)) or \
               field_name

    def as_table(self):
        """
        Returns this form rendered as HTML <tr>s -- excluding the
        <table></table>.
        """
        subs = []
        for f in self.forms.values():
            subs.append(f.as_table())
        return "\n".join(subs)

    def as_ul(self):
        """
        Returns this form rendered as HTML <li>s -- excluding the <ul></ul>.
        """
        subs = []
        for f in self.forms.values():
            subs.append(f.as_ul())
        return "\n".join(subs)

    def as_p(self):
        """
        Returns this form rendered as HTML <p>s.
        """
        subs = []
        for f in self.forms.values():
            subs.append(f.as_p())
        return "\n".join(subs)

    def _errors(self):
        """
        Returns an ErrorDict for self.data
        """
        if self.__errors is None:
            error_dict = self.forms['_self'].errors
            for k,f in self.forms.items():
                if k == '_self':
                    continue
                error_dict[k] = f.errors
            self.__errors = error_dict
        return self.__errors
    errors = property(_errors)

    def non_field_errors(self):
        """
        Returns an ErrorList of errors that aren't associated with a particular
        field -- i.e., from Form.clean(). Returns an empty ErrorList if there
        are none.
        """
        return self.errors.get(NON_FIELD_ERRORS, ErrorList())

    def _cleaned_data(self):
        if not hasattr(self, '__cleaned_data'):
            cleaned_data = {}
            errors = False
            for k, f in self.forms.items():
                if hasattr(f, 'cleaned_data'):
                    if k == '_self':
                        cleaned_data.update(f.cleaned_data)
                    else:
                        cleaned_data[k] = f.cleaned_data
                else:
                    if isinstance(f, SubForm) and f.ignore_errors():
                        continue
                    else:
                        raise AttributeError, 'cleaned_data'
            self.__cleaned_data = cleaned_data
        return self.__cleaned_data
    cleaned_data = property(_cleaned_data)

class SuperForm(BaseSuperForm):
    __metaclass__ = DeclarativeSubFormsMetaclass

if __name__ == "__main__":
    import doctest
    doctest.testmod()