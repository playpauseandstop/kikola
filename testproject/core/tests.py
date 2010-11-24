import datetime

from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.http import HttpRequest
from django.template.defaultfilters import date
from django.test import TestCase

from kikola.core.context_processors import path
from kikola.core.decorators import memoized, smart_datetime
from kikola.shortcuts import conf


DATETIME_FORMAT = conf('DATETIME_FORMAT', 'F d, H:i')
DAY = datetime.timedelta(days=1)
DEFAULT_CHARSET = conf('DEFAULT_CHARSET')
NOW = datetime.datetime.now()
TIME_FORMAT = conf('TIME_FORMAT', 'H:i')
TODAY = datetime.date.today()
YESTERDAY = TODAY - DAY

TEST_DATETIME_FORMAT = 'Y-m-d H:i:s'
TEST_SITE_DOMAIN = 'www.google.com'
TEST_SITE_NAME = 'Google'
TEST_TIME_FORMAT = 'G:i:s'


class TestContextProcesors(TestCase):

    def test_path(self):
        # Test work with empty or corrupted HttpRequest instance
        request = HttpRequest()
        request.META = {'SERVER_NAME': 'www.google.com',
                        'SERVER_PORT': 80}
        context = path(request)
        self.assertEqual(context,
                         {'REQUEST_ABSOLUTE_URI': 'http://www.google.com',
                          'REQUEST_FULL_PATH': '',
                          'REQUEST_PATH': ''})

        # Check how it works on real request
        url = reverse('context_processors_path')
        response = self.client.get(url)
        self.assertContains(response,
                            '"REQUEST_ABSOLUTE_URI": "http://testserver%s' % \
                            url)
        self.assertContains(response,
                            '"REQUEST_FULL_PATH": "%s"' % url)
        self.assertContains(response,
                            '"REQUEST_PATH": "%s"' % url)

        response = self.client.get(url, {'q': 'Query'})
        self.assertContains(response,
                            '"REQUEST_ABSOLUTE_URI": "http://testserver' \
                            '%s?q=Query"' % url)
        self.assertContains(response,
                            '"REQUEST_FULL_PATH": "%s?q=Query"' % url)
        self.assertContains(response,
                            '"REQUEST_PATH": "%s"' % url)


class TestDecorators(TestCase):

    counter = 0

    @memoized
    def count_it(self, delta=None):
        self.counter += delta or 1

    @smart_datetime
    def now(self):
        return NOW

    @smart_datetime(compare_date=YESTERDAY)
    def now_compare_to_yesterday(self):
        return NOW

    @smart_datetime(compare_date=YESTERDAY,
                    datetime_format=TEST_DATETIME_FORMAT)
    def now_compare_to_yesterday_with_datetime_format(self):
        return NOW

    @smart_datetime(time_format=TEST_TIME_FORMAT)
    def now_with_time_format(self):
        return NOW

    @smart_datetime
    def today(self):
        return TODAY

    @smart_datetime
    def yesterday_time(self):
        return NOW - DAY

    @smart_datetime(datetime_format=TEST_DATETIME_FORMAT)
    def yesterday_time_with_datetime_format(self):
        return NOW - DAY

    def test_memoized(self):
        self.count_it()
        self.count_it()

        self.count_it(1)
        self.count_it(1)
        self.count_it(1)

        self.count_it(2)

        self.assertEqual(self.counter, 4)

    def test_render_to(self):
        url = reverse('decorators_render_to')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'],
                         'text/html; charset=%s' % DEFAULT_CHARSET)
        self.assertContains(response, 'It works!', count=2)

        url = reverse('decorators_render_to_with_mimetype')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/plain')
        self.assertContains(response, 'It works!', count=1)

        url = reverse('decorators_render_to_with_mimetype_in_dict')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/plain')
        self.assertContains(response, 'It works!', count=1)

    def test_render_to_json(self):
        url = reverse('decorators_render_to_json')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertContains(response, '{}')

        url = reverse('decorators_render_to_json_with_options')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertContains(response, '    "key": "value"')

    def test_smart_datetime(self):
        self.assertEqual(self.today(), TODAY)

        self.assertEqual(self.now(), date(NOW, TIME_FORMAT))
        self.assertEqual(self.now_compare_to_yesterday(),
                         date(NOW, DATETIME_FORMAT))
        self.assertEqual(self.now_compare_to_yesterday_with_datetime_format(),
                         date(NOW, TEST_DATETIME_FORMAT))
        self.assertEqual(self.now_with_time_format(),
                         date(NOW, TEST_TIME_FORMAT))

        self.assertEqual(self.yesterday_time(),
                         date(NOW - DAY, DATETIME_FORMAT))
        self.assertEqual(self.yesterday_time_with_datetime_format(),
                         date(NOW - DAY, TEST_DATETIME_FORMAT))


class TestSitemaps(TestCase):

    def test_index_sitemap(self):
        site = Site.objects.get_current()
        site.name = TEST_SITE_NAME
        site.domain = TEST_SITE_DOMAIN
        site.save()

        url = reverse('index_sitemap')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/xml')
        self.assertContains(response,
                            '<url><loc>http://%s/</loc><changefreq>daily' \
                            '</changefreq><priority>1.0</priority></url>' % \
                            TEST_SITE_DOMAIN)
