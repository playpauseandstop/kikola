"""
kikola.templatetags.json_filters
================================

Installation
============

Adds ``kikola`` to your project's ``settings`` ``INSTALLED_APPS`` var.

jsonify
-------

Custom template tag ``jsonify`` based on skam's snippet and comments for it.
http://www.djangosnippets.org/snippets/201/

Usage
~~~~~

In templates::

    {% load json_filters %}
    <pre class="python">{{ var|safe }}</pre>
    <pre class="json">{{ var|jsonify|safe }}</pre>

And when::

    var = {
        'bool': True,
        'list': ['foo', 'bar'],
        'string': 'bar',
    }

This outputs::

    <pre class="python">{'list': ['foo', 'bar'], 'bool': True, 'string': 'bar'}</pre>
    <pre class="json">{"list": ["foo", "bar"], "bool": true, "string": "bar"}</pre>

"""

from django.core.serializers.json import DjangoJSONEncoder
from django.template import Library
from django.utils import simplejson


register = Library()


def do_jsonify(obj, safe=False):
    return simplejson.dumps(obj, cls=DjangoJSONEncoder)
register.filter('jsonify', do_jsonify)
