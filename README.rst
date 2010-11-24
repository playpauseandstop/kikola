======
kikola
======

Collection of Django's custom context processors, form fields and widgets,
middlewares, model fields, reusable apps and template tags.

Requirements
============

* Python_ 2.5 or higher
* Django_ 1.0 or higher

.. _Python: http://www.python.org/
.. _Django: http://www.djangoproject.com/

Installation
============

*On most UNIX-like systems, you'll probably need to run these commands as root
or using sudo.*

To install use::

    $ pip install kikola

Or::

    $ python setup.py install

Also, you can retrieve fresh version of ``kikola`` from `GitHub
<http://github.com/playpauseandstop/kikola>`_::

    $ git clone git://github.com/playpauseandstop/kikola.git

and place ``kikola`` directory somewhere to ``PYTHONPATH`` (or ``sys.path``).

License
=======

``kikola`` is licensed under the `BSD License
<http://github.com/playpauseandstop/kikola/blob/master/LICENSE>`_.


Contents
========

Now ``kikola`` project consist of:

- contrib

  - basicsearch

- core

  - context_processors

    - path

  - decorators

    - memoized
    - render_to
    - render_to_json
    - smart_datetime

  - sitemaps

    - IndexSitemap

- db

  - fields

    - JSONField
    - MonthField
    - PickleField
    - TimeDeltaField
    - URLField

- forms

  - fields

    - JSONField
    - TimeDeltaField
    - URLField

  - forms

    - TabbedForm

  - widgets

    - AutocompleteWidget
    - JSONWidget
    - SelectDateWidget
    - TimeDeltaWidget

- middleware

  - locale

    - SmartMultilingualMiddleware

- shortcuts

  - conf

- templatetags

  - json_tags

    - jsonify

  - timedelta_tags

    - timedelta

  - twitter_tags

    - twitterize

- utils

  - digits

    - force_int

  - timedelta

    - TimedeltaJSONEncoder
    - str_to_timedelta
    - timedelta_average
    - timedelta_div
    - timedelta_seconds
    - timedelta_to_str

More
====

Found a bug? Have a good idea for improving kikola? Head over to `GitHub`_ to
create a new issue or fork.
