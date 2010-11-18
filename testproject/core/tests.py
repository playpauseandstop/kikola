from django.utils.unittest import TestCase

from kikola.core.decorators import memoized


class TestDecorators(TestCase):

    counter = 0

    @memoized
    def count_it(self, delta=None):
        self.counter += delta or 1

    def test_memoized(self):
        self.count_it()
        self.count_it()

        self.count_it(1)
        self.count_it(1)
        self.count_it(1)

        self.count_it(2)

        self.assertEqual(self.counter, 4)
