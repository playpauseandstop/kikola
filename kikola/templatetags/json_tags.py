"""
=============================
kikola.templatetags.json_tags
=============================

Template filter to dumps Python var to JSON in templates.

Installation
============

Just add ``kikola`` to ``INSTALLED_APPS`` var of your project settings.

Filters
=======

jsonify
-------

Custom template filter ``jsonify`` based on `skam's snippet
<http://www.djangosnippets.org/snippets/201/>`_ and comments for it.

Don't forget to make resulted variable ``safe`` to use it inside textareas.

Usage
~~~~~

In templates::

    {% load json_tags %}
    <pre class="python">{{ var|safe }}</pre>
    <pre class="json">{{ var|jsonify|safe }}</pre>

And when::

    var = {
        'bool': True,
        'list': ['foo', 'bar'],
        'string': 'bar',
    }

Template renders as::

    <pre class="python">{'list': ['foo', 'bar'], 'bool': True, 'string': 'bar'}</pre>
    <pre class="json">{"list": ["foo", "bar"], "bool": true, "string": "bar"}</pre>

"""

from django.core.serializers.json import DjangoJSONEncoder
from django.template import Library
from django.utils import simplejson


register = Library()


@register.filter
def jsonify(obj, safe=False):
    return simplejson.dumps(obj, cls=DjangoJSONEncoder)
