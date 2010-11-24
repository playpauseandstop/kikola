import datetime

try:
    import json
except ImportError:
    from django.utils import simplejson as json

from functools import partial, wraps

from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.defaultfilters import date as date_filter

from kikola.shortcuts import conf


__all__ = ('memoized', 'render_to', 'render_to_json', 'smart_datetime')


TODAY = datetime.date.today


class memoized(object):
    """
    Decorator that caches a function's return value each time it is called.
    If called later with the same arguments, the cached value is returned, and
    not re-evaluated.

    Original posted on: http://wiki.python.org/moin/PythonDecoratorLibrary
    """
    def __init__(self, func):
        self.cache = {}
        self.func = func

    def __call__(self, *args):
        try:
            return self.cache[args]
        except KeyError:
            value = self.func(*args)
            self.cache[args] = value
            return value
        except TypeError:
            # uncachable -- for instance, passing a list as an argument.
            # Better to not cache than to blow up entirely.
            return self.func(*args)

    def __get__(self, obj, objtype):
        """
        Support instance methods.
        """
        return partial(self.__call__, obj)

    def __repr__(self):
        """
        Return the function's docstring.
        """
        return self.func.__doc__


def render_to(template_path, mimetype=None):
    """
    Expect the dict from view. Render returned dict with RequestContext.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            output = func(request, *args, **kwargs)

            if not isinstance(output, dict):
                return output

            kwargs = {'context_instance': RequestContext(request)}
            output['request'] = request

            if 'MIME_TYPE' in output:
                kwargs['mimetype'] = output.pop('MIME_TYPE')
            elif 'MIMETYPE' in output:
                kwargs['mimetype'] = output.pop('MIMETYPE')
            elif mimetype:
                kwargs['mimetype'] = mimetype

            if 'TEMPLATE' in output:
                template = output.pop('TEMPLATE')
            else:
                template = template_path

            return render_to_response(template, output, **kwargs)
        return wrapper
    return decorator


def render_to_json(*args, **json_kwargs):
    """
    Render output from view function as JSON response.
    """
    def json_decorator(func, **json_kwargs):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            # Execute view function
            output = func(request, *args, **kwargs)

            # Prepare JSON kwargs
            defaults = {'cls': DjangoJSONEncoder,
                        'ensure_ascii': False}
            defaults.update(json_kwargs)

            # Dumps view function output into JSON response
            return HttpResponse(json.dumps(output, **defaults),
                                mimetype='application/json')
        return wrapper

    if not args and not json_kwargs:
        return json_decorator

    if args and callable(args[0]):
        return json_decorator(args[0], **json_kwargs)

    def decorator(func):
        return json_decorator(func, **json_kwargs)
    return decorator


def smart_datetime(datetime_format=None, time_format=None, compare_date=None):
    """
    Format ``datetime.datetime`` or compatible object returned by ``func`` with
    ``django.templates.defaultfilters.date`` filter.

    If this date is same day to today - use ``time_format`` format called with
    decorator or "H:i" by default.

    Else - use ``datetime_format`` called with decorator or "F d, H:i" by
    default.

    Also, you can to compare returned datetime with other date, not today,
    by sending it as ``compare_date`` arg.
    """
    def datetime_decorator(func, datetime_format=None, time_format=None,
                           compare_date=None):
        compare_date = compare_date or TODAY()
        datetime_format = \
            datetime_format or conf('DATETIME_FORMAT', 'F d, H:i')
        time_format = time_format or conf('TIME_FORMAT', 'H:i')

        @wraps(func)
        def wrapper(*args, **kwargs):
            value = func(*args, **kwargs)

            if not hasattr(value, 'date'):
                return value

            if value.date() == compare_date:
                format = time_format
            else:
                format = datetime_format

            return date_filter(value, format)
        return wrapper

    if datetime_format and callable(datetime_format):
        return datetime_decorator(datetime_format)

    if datetime_format is None and \
       time_format is None and \
       compare_date is None:
        return datetime_decorator

    def decorator(func):
        return datetime_decorator(func,
                                  datetime_format,
                                  time_format,
                                  compare_date)
    return decorator
