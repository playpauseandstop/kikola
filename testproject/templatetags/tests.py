from django.template import Context, Template
from django.utils.html import escape
from django.utils.unittest import TestCase


TEST_JSONIFY_TEMPLATE = '{{ var|jsonify }}'
TEST_JSONIFY_VARS = (
    (False, 'false'),
    (None, 'null'),
    (True, 'true'),
    (0, '0'),
    (0.0, '0.0'),
    ('text', '"text"'),
    ([1, 2, 3], '[1, 2, 3]'),
    ({'a': 1}, '{"a": 1}'),
)
TEST_TWITTERIZE_TEMPLATE = '{{ text|twitterize }}'
TEST_TWITTERIZE_VARS = (
    ('@playpausenstop is my man!',
     '@<a href="http://twitter.com/playpausenstop" rel="nofollow">' \
     'playpausenstop</a> is my man!'),
    ('RT @playpausenstop: Chromed Bird rocks!',
     '<span class="retweeted">RT</span> ' \
     '@<a href="http://twitter.com/playpausenstop" rel="nofollow">' \
     'playpausenstop</a>: Chromed Bird rocks!'),
    ('Use Google Luke! http://www.google.com/',
     'Use Google Luke! <a href="http://www.google.com/" rel="nofollow">' \
     'http://www.google.com/</a>'),
    ('Bag Raiders - Way Back Home #nowplaying',
     'Bag Raiders - Way Back Home <a href="http://twitter.com/search?q=' \
      '%23nowplaying" rel="nofollow">#nowplaying</a>'),
)


class TestTemplateTags(TestCase):

    def test_jsonify(self):
        template = Template('{% load json_tags %}' + TEST_JSONIFY_TEMPLATE)

        for var, rendered in TEST_JSONIFY_VARS:
            context = Context({'var': var})
            self.assertEqual(template.render(context), escape(rendered))

    def test_twitterize(self):
        template = Template('{% load twitter_tags %}' + \
                            TEST_TWITTERIZE_TEMPLATE)

        for text, rendered in TEST_TWITTERIZE_VARS:
            context = Context({'text': text})
            self.assertEqual(template.render(context), rendered)
