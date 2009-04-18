from django.shortcuts import render_to_response
from django.template import RequestContext

from settings import *
from utils import *


def search(request):
    context = RequestContext(request)
    form_cls = load_cls(SEARCH_FORM)

    if 'query' in request.REQUEST:
        form = form_cls(request.REQUEST, request=request)

        if form.is_valid():
            context.update(form.search())
    else:
        form = form_cls(request=request)

    context.update({'form': form})
    return render_to_response(SEARCH_TEMPLATE_NAME, context)
