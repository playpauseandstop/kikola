from django.conf.urls.defaults import *


urlpatterns = patterns('testproject.utils.views',
    url(r'^timedelta-json-encoder/', 'timedelta_json_encoder',
        name='timedelta_json_encoder'),
)
