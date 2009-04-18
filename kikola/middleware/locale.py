from django.conf import settings
from django.http import HttpResponseRedirect
from django.utils.translation import check_for_language


class SmartMultilingualMiddleware(object):
    """
    kikola.core.middleware.SmartMultilingualMiddleware
    ==================================================

    If you use internationalization for your Django project and has more than
    one language - Django would be auto detected default language by user-agent
    settings. This middleware disables this and your site always opened with
    ``settings.LANGUAGE_CODE`` localization.

    If you want to change site localization, modify default locale changing
    mechanizm for your project::

        from django.conf import settings
        from django.http import HttpResponseRedirect
        from django.utils.translation import check_for_language


        def set_language(request, code, next=None):
            next = next or '/'
            next = request.REQUEST.get('next',
                                       request.META.get('HTTP_REFERER', next))

            response = HttpResponseRedirect(next)

            if code and check_for_language(code):
                if hasattr(request, 'session'):
                    request.session['django_language'] = code
                    request.session['kikola_language'] = code
                else:
                    response.set_cookie(settings.LANGUAGE_COOKIE_NAME, code)
                    response.set_cookie('kikola_language', code)

            return response

    To enable, appends ``kikola.core.middleware.SmartMultilingualMiddleware``
    to your project's ``settings`` ``MIDDLEWARE_CLASSES`` var.
    """
    def process_request(self, request):
        language_code = settings.LANGUAGE_CODE
        old = language_code

        if language_code and check_for_language(language_code):
            if hasattr(request, 'session'):
                if not 'kikola_language' in request.session:
                    request.session['django_language'] = language_code
                language_code = request.session['django_language']
            else:
                if not request.has_cookie('kikola_language'):
                    request.set_cookie('django_language', language_code)
                language_code = request.COOKIE.get('django_language')

            # Set up ``DEFAULT_LANGUAGE`` var for ``django-multilingual``
            if hasattr(settings, 'DEFAULT_LANGUAGE'):
                settings.DEFAULT_LANGUAGE = \
                    [k for k, v in settings.LANGUAGES].index(language_code) + 1

        if language_code != old:
            return HttpResponseRedirect(request.path)
