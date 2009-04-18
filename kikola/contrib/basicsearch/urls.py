from django.conf.urls.defaults import *


urlpatterns = patterns('kikola.contrib.basicsearch.views',
    url(r'^$', 'search', name='basicsearch'),
)
