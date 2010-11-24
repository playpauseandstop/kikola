from django.conf.urls.defaults import *

from kikola.core.sitemaps import IndexSitemap


sitemaps = {
    'index': IndexSitemap(priority=1.0, changefreq='daily'),
}


urlpatterns = patterns('testproject.core.views',
    url(r'^context-processors/path/$', 'context_processors_path',
        name='context_processors_path'),
    url(r'^decorators/render-to/$', 'decorators_render_to',
        name='decorators_render_to'),
    url(r'^decorators/render-to/mimetype/$',
        'decorators_render_to_with_mimetype',
        name='decorators_render_to_with_mimetype'),
    url(r'^decorators/render-to-json/$', 'decorators_render_to_json',
        name='decorators_render_to_json'),
    url(r'^decorators/render-to-json/options/$',
        'decorators_render_to_json_with_options',
        name='decorators_render_to_json_with_options'),
)

urlpatterns += patterns('django.contrib.sitemaps.views',
    (r'^sitemap\.xml', 'sitemap', {'sitemaps': sitemaps}, 'index_sitemap'),
)
