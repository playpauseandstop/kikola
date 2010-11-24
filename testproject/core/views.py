from kikola.core.context_processors import path
from kikola.core.decorators import render_to, render_to_json


@render_to_json
def context_processors_path(request):
    return path(request)


@render_to('core/render_to.html')
def decorators_render_to(request):
    return {'text': 'It works!'}


@render_to('core/render_to.txt', mimetype='text/plain')
def decorators_render_to_with_mimetype(request):
    return {'text': 'It works!'}


@render_to('core/render_to.html')
def decorators_render_to_with_mimetype_in_dict(request):
    return {'MIMETYPE': 'text/plain',
            'TEMPLATE': 'core/render_to.txt',
            'text': 'It works!'}


@render_to_json
def decorators_render_to_json(request):
    return {}


@render_to_json(indent=4)
def decorators_render_to_json_with_options(request):
    return {'key': 'value'}
