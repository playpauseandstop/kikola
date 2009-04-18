from django.contrib.sitemaps import Sitemap


__all__ = ('IndexSitemap', )


class IndexSitemap(Sitemap):
    """
    kikola.core.sitemaps.IndexSitemap
    =================================

    Adds only index page ``/`` to your sitemap collection.

    Usage (in your project's ``ROOT_URLCONF`` module)::

        from django.conf.urls.defaults import *
        from django.contrib.flatpages.models import FlatPage
        from django.contrib.sitemaps import GenericSitemap

        from kikola.core.sitemaps import IndexSitemap


        sitemaps = {
            'index': IndexSitemap(priority=1.0, changefreq='weekly'),
            'pages': GenericSitemap({
                'queryset': FlatPage.objects.all(),
            }, priority=0.6, changefreq='monthly'),
        }

        urlpatterns = patterns(
            url(r'^$', 'project.views.index', name='index')
            (r'^sitemap.xml$', 'django.contrib.sitemaps.views.sitemap',
                {'sitemaps': sitemaps}, 'sitemap'),
        )

    """
    def __init__(self, priority=None, changefreq=None):
        self.changefreq, self.priority = changefreq, priority

    def location(self, obj):
        return obj

    def items(self):
        return ['/']
