def path(request):
    """
    kikola.core.context_processors.path
    ===================================

    Adds current path and full path variables to templates.

    To enable, adds ``kikola.core.context_processors.path`` to your project's
    ``settings`` ``TEMPLATE_CONTEXT_PROCESSORS`` var.

    **Note:** Django has ``django.core.context_processors.request`` context
    processor that adding current ``HttpRequest`` object to templates.
    """
    return {'REQUEST_FULL_PATH': request.get_full_path(),
            'REQUEST_PATH': request.path}
