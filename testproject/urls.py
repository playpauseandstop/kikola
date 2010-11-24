from django import VERSION
from django.conf.urls.defaults import *
from django.contrib import admin


admin.autodiscover()


if VERSION[0] == 1 and VERSION[1] == 0:
    urlpatterns = patterns('',
        (r'^admin/(.*)', admin.site.root),
    )
else:
    urlpatterns = patterns('',
        (r'^admin/', include(admin.site.urls)),
    )


urlpatterns += patterns('',
    (r'^utils/', include('testproject.utils.urls')),
)
