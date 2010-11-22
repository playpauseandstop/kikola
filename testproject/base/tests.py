from django.utils.unittest import TestCase

from kikola import get_version


class TestKikola(TestCase):

    def test_get_version(self):
        self.assertEqual(get_version((0, 1)), '0.1')
        self.assertEqual(get_version((0, 1, None)), '0.1')
        self.assertEqual(get_version((0, 1, 'alpha')), '0.1-alpha')
        self.assertEqual(get_version((0, 1, 1)), '0.1.1')
