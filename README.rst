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
    - PickleField
    - URLField

- forms

  - fields

    - URLField

  - widgets

    - AutocompleteWidget
    - JSONWidget
    - SelectDateWidget
    - SpanWidget

- middleware

  - locale

    - SmartMultilingualMiddleware

- templatetags

  - json_tags

    - jsonify

  - twitter_tags

    - twitterize

More
====

Found a bug? Have a good idea for improving kikola? Head over to `GitHub`_ to
create a new issue or fork.
