from settings_common import *


# Databases settings
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': rel('testproject.db'),
    },
}

# Debug settings
DEBUG = True
TEMPLATE_DEBUG = DEBUG


try:
    from settings_local import *
except ImportError:
    pass
