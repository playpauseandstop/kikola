from settings import *


# Debug settins
DEBUG = True
TEMPLATE_DEBUG = DEBUG


# Fix logging settings
LOGGING['loggers'].update({
    'django.db.backends': {
        'handlers': ['null'],
        'level': 'DEBUG',
        'propagate': False,
    },
})


try:
    from settings_testing_local import *
except ImportError:
    pass
