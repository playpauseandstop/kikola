======
kikola
======

1. Introduction_
2. Requirements_
3. Installation_
4. Contents_
5. More_

----

Introduction
============

Kikola_ is a collection of Django's custom context processors, form fields
and widgets, middlewares, model fields, reusable apps and template tags.

.. _Kikola: http://github.com/playpauseandstop/kikola

Requirements
============

* Django_ (>=1.0)

.. _Django: http://www.djangoproject.com/

Installation
============

You can install ``kikola`` via::

    sudo python setup.py install

from ``kikola`` root directory. Also you can to install ``kikola`` via
`easy_install`_::

    sudo easy_install kikola

To use latest version of ``kikola`` in your projects, clone ``kikola`` git_
repository::

    git clone git://github.com/playpauseandstop/kikola.git

and add ``kikola`` directory path to your ``PYTHONPATH``.

.. _`easy_install`: http://pypi.python.org/pypi/setuptools
.. _git: http://git.or.cz/

Contents
========

Now ``kikola`` project consist of:

- core

  - context_processors

    - path

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

  - json_filters

    - jsonify

More
====

If you find bug in Kikola, please send it via `GitHub issues`_.

.. _`GitHub issues`: http://github.com/playpauseandstop/kikola/issues
