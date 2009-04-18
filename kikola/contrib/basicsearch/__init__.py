"""
==========================
kikola.contrib.basicsearch
==========================

Application to lightweight search over models, existed in your project.

Installation
============

1. Add ``kikola.contrib.basicsearch`` to your project's ``settings``
   ``INSTALLED_APPS`` var.

2. Set up ``SEARCH_MODELS`` var in your project's ``settings`` module. (see
   default config for ``SEARCH_MODELS`` below_)

3. Include ``kikola.contrib.basicsearch.urls`` in your project's
   ``ROOT_URLCONF`` module::

       from django.conf.urls.defaults import *


       urlpatterns = patterns('',
           (r'^search/', include('kikola.contrib.basicsearch.urls')),
       )

4. Go to search url and enjoy :)

.. _below: `SEARCH_MODELS`_

Configuration
=============

You can customize ``basicsearch`` application by next setting vars

SEARCH_FORM
-----------

Full path to default ``SearchForm`` class.

By default uses ``kikola.contrib.basicsearch.forms.SearchForm`` class.

SEARCH_MODELS
-------------

**Required.** Sets up models for searching. For example to search over
Django's FlatPages use next config::

    SEARCH_MODELS = {
        # Use same format as ``app_label`` in serialized data
        'flatpages.FlatPage': {
            # Object description in search results
            'description': '{{ obj.content|truncatewords_html:20 }}',

            # Object fields to search
            'fields': ('title', 'content'),

            # Use fulltext search (use this only when
            # ``settings.DATABASE_ENGINE == 'mysql'``)
            'fulltext': False,

            # Object link in search results (by default
            # ``{{ obj.get_absolute_url }}`` used)
            'link': '{% url flatpage obj.url %}',

            # Priority. Useful when search not over one model. Objects with
            # higher priority rendering first in search results.
            'priority': 0,

            # Object title in search results (by default ``{{ obj }}`` used)
            'title': '{{ obj.title }}',

            # Trigger. Custom filter to found search results. For example,
            # current trigger enables search only over flatpages with
            # ``enable_comments``.
            #
            # To disable trigger, set ``'trigger': None``
            'trigger': lambda obj: obj.enable_comments,
        }
    }

SEARCH_NOT_FOUND_MESSAGE
------------------------

Default search "not found" message. By default: ``Any objects was found by
your query.``

SEARCH_QUERY_MIN_LENGTH
-----------------------

Minimal length of search query. By default: 3.

SEARCH_QUERY_MAX_LENGTH
-----------------------

Maximal length of search query. By default: 64.

SEARCH_RESULTS_PER_PAGE
-----------------------

Number of search results, rendering at search page. By default: 10.

SEARCH_TEMPLATE_NAME
--------------------

Template used for rendering search results. By default:
``basicsearch/search.html``.

"""
