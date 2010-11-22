"""
================================
kikola.templatetags.twitter_tags
================================

Additional filter to parse twitter statuses in Django templates.

Installation
============

Just add ``kikola`` to ``INSTALLED_APPS`` var of your project settings.

Filters
=======

twitterize
----------

Workaround to parse twitter statuses in Django templates. This filter:

* Urlize status using default Django template filter
* Wraps "RT" to special ``<span>`` tag
* Process ``@username`` as link to username's timeline
* Process ``#tag`` as link to tag's search

Usage
~~~~~

Just add ``twitterize`` filter to rendering twitter status, like there::

    {% load twitter_tags %}
    <ul>
        {% for status in statuses %}
        <li>{{ status|twitterize }}
        {% endfor %}
    </ul>

And if,

::

    statuses = [
        'RT @playpauseandstop: Chromed Bird rocks!',
        'Use Google Luke! http://www.google.com/',
        'Bag Raiders - Way Back Home #nowplaying',
    ]

Django rendered first template, as like this::

    <ul>
        <li>
            <span class="retweeted">RT</span>
            @<a href="http://twitter.com/playpauseandstop" rel="nofollow">
            playpauseandstop</a>: Chromed Bird rocks!
        </li>
        <li>
            Use Google Luke!
            <a href="http://www.google.com/" rel="nofollow">
            http://www.google.com/</a>
        </li>
        <li>
            Bag Raiders - Way Back Home
            <a href="http://twitter.com/search?q=%23nowplaying" rel="nofollow">
            #nowplaying</a>
        </li>
    </ul>

"""

import re

from django.template import Library
from django.template.defaultfilters import stringfilter
from django.utils.html import urlize
from django.utils.safestring import mark_safe


register = Library()


@register.filter
@stringfilter
def twitterize(status, autoescape=None):
    # Urlize present links
    status = urlize(status, nofollow=True, autoescape=autoescape)

    # Wraps "RT" text in status
    status = re.sub(r'^RT @', '<span class="retweeted">RT</span> @', status)

    # Add links to twitter usernames
    status = re.sub(r'(\s|^)@([a-zA-Z0-9_]+)',
                    '\\1@<a href="http://twitter.com/\\2" rel="nofollow">' \
                    '\\2</a>',
                    status)

    # Add links to hash tags
    status = re.sub(r'(\s|^)#([a-zA-Z0-9_]+)',
                    '\\1<a href="http://twitter.com/search?q=%23\\2" ' \
                    'rel="nofollow">#\\2</a>',
                    status)

    return mark_safe(status)

twitterize.is_safe = True
twitterize.needs_autoescape = True
