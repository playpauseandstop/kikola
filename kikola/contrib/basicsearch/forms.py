from django import forms
from django.conf import settings
from django.core.paginator import InvalidPage, Paginator
from django.db.models import Q, get_model
from django.template import Context, Template
from django.utils.translation import ugettext as _

from settings import *


__all__ = ('SearchForm', )


class SearchForm(forms.Form):
    query = forms.CharField(label=_('Search query'),
        min_length=SEARCH_QUERY_MIN_LENGTH, max_length=SEARCH_QUERY_MAX_LENGTH)

    def __init__(self, *args, **kwargs):
        if not 'request' in kwargs:
            raise TypeError, 'Please, supply `request` keyword argument first.'

        self.request = kwargs.pop('request')
        super(SearchForm, self).__init__(*args, **kwargs)

    def search(self):
        page = self.request.REQUEST.get('page', 1)
        per_page = self.request.REQUEST.get('per_page',
                                            SEARCH_RESULTS_PER_PAGE)
        query = self.cleaned_data['query']
        search_results = []

        result_dict = {'search_query': query}

        for model_name, options in SEARCH_MODELS.items():
            assert 'fields' in options, \
                   'Please, set up fields options for "%s".' % modelname

            app_label, model_name = model_name.split('.')
            model = get_model(app_label, model_name)

            description = options.get('description', False)
            fields = options['fields']
            fulltext = options.get('fulltext', False)
            link = options.get('link', False)
            priority = options.get('priority', 0)
            title = options.get('title', '{{ obj }}')
            trigger = options.get('trigger', None)

            if fulltext and settings.DATABASE_ENGINE == 'mysql':
                lookup = '%s__search'
            else:
                lookup = '%s__icontains'

            search_lookup = None

            for field in fields:
                if search_lookup is None:
                    search_lookup = Q(**{lookup % field: query})
                else:
                    search_lookup |= Q(**{lookup % field: query})

            objects = model.objects.filter(search_lookup)

            if not objects:
                continue

            description_template = \
                description and Template(description) or None
            title_template = title and Template(title) or None

            for obj in objects:
                if trigger is not None and not trigger(obj):
                    continue

                context = Context({'obj': obj})

                if description_template:
                    obj_description = description_template.render(context)
                else:
                    obj_description = description

                if link_template:
                    obj_link = link_template.render(context)
                else:
                    obj_link = obj.get_absolute_url()

                if title_template:
                    obj_title = title_template.render(context)
                else:
                    obj_title = title

                search_results.append({
                    'description': obj_description,
                    'link': obj_link,
                    'obj': obj,
                    'priority': priority,
                    'title': obj_title,
                })

        if not search_results:
            result_dict.update(
                {'search_error': SEARCH_NOT_FOUND_MESSAGE}
            )
            return result_dict

        search_results.sort(cmp=lambda x, y: cmp(y['priority'], x['priority']))
        paginator = Paginator(search_results, per_page)

        try:
            page_obj = paginator.page(page)
        except InvalidPage:
            result_dict.update(
                {'search_error': SEARCH_NOT_FOUND_MESSAGE}
            )
            return result_dict

        result_dict.update({
            'search_paginator': paginator,
            'search_results': page_obj.object_list,

            'search_count': paginator.count,
            'search_is_first_page': page_obj.number == 1,
            'search_is_last_page': page_obj.number == paginator.num_pages,
            'search_has_next_page': page_obj.has_next(),
            'search_has_previous_page': page_obj.has_previous(),
            'search_next_page': page_obj.number + 1,
            'search_page': page_obj,
            'search_pages': paginator.page_range,
            'search_pages_count': paginator.num_pages,
            'search_previous_page': page_obj.number - 1,
        })
        return result_dict
