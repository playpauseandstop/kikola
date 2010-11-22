from django.utils.unittest import TestCase

from kikola.shortcuts import conf


class TestShortcuts(TestCase):

    def test_conf(self):
        self.assertFalse(conf('DEBUG'))
        self.assertRaises(AttributeError, conf, 'DEBUGIOUS')
        self.assertTrue(conf('DEBUGIOUS', True))
