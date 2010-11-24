import os

from django import VERSION


rel = lambda *x: os.path.abspath(os.path.join(os.path.dirname(__file__), *x))


# Administration settings
ADMIN_MEDIA_PREFIX = '/static/admin/'

# CSRF settings
CSRF_COOKIE_NAME = 'testproject_csrf'

# Date and time settings
FIRST_DAY_OF_WEEK = 1

if VERSION[0] == 1 and VERSION[1] >= 2:
    TIME_ZONE = None
else:
    import time
    TIME_ZONE = time.tzname[0]

# Installed applications
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sitemaps',
    'django.contrib.sites',

    'django_extensions',
    'kikola',

    'testproject.base',
    'testproject.core',
    'testproject.db',
    'testproject.templatetags',
    'testproject.shortcuts',
    'testproject.utils',
]

# Language and locale settings
USE_I18N = False
USE_L10N = False
LANGUAGE_CODE = 'en'

# Logging settings
LOGGING = {
    'disable_existing_loggers': True,
    'formatters': {
        'simple': {
            'format': '%(asctime)s %(levelname)s %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'level': 'DEBUG',
        },
        'null': {
            'class': 'django.utils.log.NullHandler',
            'level': 'DEBUG',
        }
    },
    'loggers': {
    },
    'version': 1,
}

# Login and logout settings
AUTH_PROFILE_MODULE = 'accounts.UserProfile'
LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/login/'
LOGOUT_URL = '/logout/'

# Messages settings
if VERSION[0] == 1 and VERSION[1] >= 2:
    MESSAGE_STORAGE = \
        'django.contrib.messages.storage.fallback.FallbackStorage'

# Middleware settings
MIDDLEWARE_CLASSES = [
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

# Session settings
SESSION_COOKIE_NAME = 'testproject_sid'

# Static files settings
STATIC_ROOT = rel('static')
STATIC_URL = '/static/'

# Template settings
TEMPLATE_CONTEXT_PROCESSORS = [
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.i18n',
    'django.core.context_processors.static',
]

# Other Django-related settings
ROOT_URLCONF = 'testproject.urls'
SITE_ID = 1
