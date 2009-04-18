from django.conf import settings
from django.utils.translation import ugettext as _


__all__ = ('SEARCH_FORM', 'SEARCH_MODELS', 'SEARCH_QUERY_MIN_LENGTH',
           'SEARCH_QUERY_MAX_LENGTH', 'SEARCH_RESULTS_PER_PAGE')


# Full path to default ``SearchForm`` class
SEARCH_FORM = getattr(settings,
                      'SEARCH_FORM',
                      'kikola.contrib.basicsearch.forms.SearchForm')

# Sets up models for searching
SEARCH_MODELS = getattr(settings, 'SEARCH_MODELS', {})

# Default search "not found" message
SEARCH_NOT_FOUND_MESSAGE = getattr(settings,
                                   'SEARCH_NOT_FOUND_MESSAGE',
                                   _('Any objects was found by your query.'))

# Minimal length of search query
SEARCH_QUERY_MIN_LENGTH = getattr(settings, 'SEARCH_QUERY_MIN_LENGTH', 3)

# Maximal length of search query
SEARCH_QUERY_MAX_LENGTH = getattr(settings, 'SEARCH_QUERY_MAX_LENGTH', 64)

# Number of search results, rendering at search page
SEARCH_RESULTS_PER_PAGE = getattr(settings, 'SEARCH_RESULTS_PER_PAGE', 10)

# Template used for rendering search results
SEARCH_TEMPLATE_NAME = getattr(settings,
                               'SEARCH_TEMPLATE_NAME',
                               'basicsearch/search.html')
