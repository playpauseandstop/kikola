from settings_common import *


# Databases settings
if VERSION[0] == 1 and VERSION[1] >= 2:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': rel('testproject.db'),
        },
    }
else:
    DATABASE_ENGINE = 'sqlite3'
    DATABASE_NAME = rel('testproject.db')

# Debug settings
DEBUG = True
TEMPLATE_DEBUG = DEBUG

# Fix middleware settings
if VERSION[0] == 1 and VERSION[1] < 2:
    classes = (
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
    )
    [MIDDLEWARE_CLASSES.remove(cls) for cls in classes]

# Fix template context processor settings
if VERSION[0] == 1 and VERSION[1] < 2:
    processors = (
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
        'django.core.context_processors.static',
    )
    [TEMPLATE_CONTEXT_PROCESSORS.remove(proc) for proc in processors]
    TEMPLATE_CONTEXT_PROCESSORS.append('django.core.context_processors.auth')
    TEMPLATE_CONTEXT_PROCESSORS.append('django.core.context_processors.media')
elif VERSION[0] == 1 and VERSION[1] == 2:
    TEMPLATE_CONTEXT_PROCESSORS.remove('django.core.context_processors.static')
    TEMPLATE_CONTEXT_PROCESSORS.append('django.core.context_processors.media')


try:
    from settings_local import *
except ImportError:
    pass
