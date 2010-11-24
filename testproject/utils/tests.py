import datetime

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils.encoding import smart_str

from kikola.utils import *


NOW = datetime.datetime.now()


class Dummy(object):

    def __init__(self, value):
        self.value = value


class DummyInt(Dummy):

    def __int__(self):
        return self.value


class DummyStr(Dummy):

    def __str__(self):
        return smart_str(self.value)


class TestDigits(TestCase):

    def test_force_int(self):
        self.assertEqual(force_int(1), 1)
        self.assertEqual(force_int('1'), 1)
        self.assertEqual(force_int(DummyInt(1)), 1)
        self.assertEqual(force_int(DummyStr('1')), 1)
        self.assertEqual(force_int(1.5), 1)
        self.assertEqual(force_int('1.5'), 1)
        self.assertEqual(force_int('1;5'), 1)
        self.assertEqual(force_int(' 1;5'), 1)
        self.assertEqual(force_int('data'), None)
        self.assertEqual(force_int('data', 1), 1)


class TestTimedelta(TestCase):

    def setUp(self):
        self.timedelta = datetime.timedelta()
        self.timedelta001 = datetime.timedelta(seconds=1)
        self.timedelta0400 = datetime.timedelta(minutes=40)
        self.timedelta0401 = datetime.timedelta(minutes=40, seconds=1)
        self.timedelta7350 = datetime.timedelta(hours=7, minutes=35)
        self.timedelta73510 = datetime.timedelta(hours=7,
                                                 minutes=35,
                                                 seconds=10)
        self.timedelta94730 = datetime.timedelta(hours=9,
                                                 minutes=47,
                                                 seconds=30)
        self.timedelta1200 = datetime.timedelta(hours=12)
        self.timedelta1201 = datetime.timedelta(hours=12, seconds=1)
        self.timedelta24100 = datetime.timedelta(hours=24, minutes=10)
        self.timedelta24105 = datetime.timedelta(hours=24,
                                                 minutes=10,
                                                 seconds=5)
        self.timedelta27410 = datetime.timedelta(hours=27, minutes=41)
        self.timedelta274114 = datetime.timedelta(hours=27,
                                                  minutes=41,
                                                  seconds=14)
        self.timedelta16800 = datetime.timedelta(hours=168)
        self.timedelta433280 = datetime.timedelta(hours=433, minutes=28)
        self.timedelta433287 = datetime.timedelta(hours=433,
                                                  minutes=28,
                                                  seconds=7)

    def test_str_to_timedelta(self):
        self.assertRaises(ValueError,
                          str_to_timedelta,
                          self.timedelta)

        self.assertEqual(str_to_timedelta('00:00'), self.timedelta)
        self.assertEqual(str_to_timedelta('00:00:01'), self.timedelta001)
        self.assertEqual(str_to_timedelta('00:40'), self.timedelta0400)
        self.assertEqual(str_to_timedelta('00:40:01'), self.timedelta0401)
        self.assertEqual(str_to_timedelta('7:35'), self.timedelta7350)
        self.assertEqual(str_to_timedelta('7:35:10'), self.timedelta73510)
        self.assertEqual(str_to_timedelta('07:35'), self.timedelta7350)
        self.assertEqual(str_to_timedelta('07:35:10'), self.timedelta73510)
        self.assertEqual(str_to_timedelta('12:00'), self.timedelta1200)
        self.assertEqual(str_to_timedelta('12:00:01'), self.timedelta1201)
        self.assertEqual(str_to_timedelta('27:41'), self.timedelta27410)
        self.assertEqual(str_to_timedelta('27:41:14'), self.timedelta274114)
        self.assertEqual(str_to_timedelta('2009-10-21 12:00'), None)
        self.assertEqual(str_to_timedelta('1d 3:41'), self.timedelta27410)
        self.assertEqual(str_to_timedelta('1 day, 3:41'), self.timedelta27410)
        self.assertEqual(str_to_timedelta('1d 3:41:14'), self.timedelta274114)
        self.assertEqual(str_to_timedelta('1 day, 3:41:14'),
                         self.timedelta274114)
        self.assertEqual(str_to_timedelta('2w 4d 1:28'), self.timedelta433280)
        self.assertEqual(str_to_timedelta('2 weeks, 4 days, 1:28'),
                         self.timedelta433280)
        self.assertEqual(str_to_timedelta('18 days, 1:28'),
                         self.timedelta433280)
        self.assertEqual(str_to_timedelta('2w 4d 1:28:07'),
                         self.timedelta433287)
        self.assertEqual(str_to_timedelta('2 weeks, 4 days, 1:28:07'),
                         self.timedelta433287)
        self.assertEqual(str_to_timedelta('18 days, 1:28:07'),
                         self.timedelta433287)

    def test_timedelta_average(self):
        avg = timedelta_average(self.timedelta0400, self.timedelta0400)
        self.assertEqual(avg, self.timedelta0400)

        avg = timedelta_average(self.timedelta7350, self.timedelta1200)
        self.assertEqual(avg, self.timedelta94730)

    def test_timedelta_average_list_or_tuple(self):
        avg = timedelta_average((self.timedelta0400, self.timedelta0400))
        self.assertEqual(avg, self.timedelta0400)

        avg = timedelta_average([self.timedelta0400, self.timedelta0400])
        self.assertEqual(avg, self.timedelta0400)

    def test_timedelta_div(self):
        result = timedelta_div(self.timedelta1200, self.timedelta)
        self.assertEqual(result, None)

        result = timedelta_div(self.timedelta16800, self.timedelta1200)
        self.assertEqual(result, 14.0)

    def test_timedelta_json_encoder(self):
        url = reverse('timedelta_json_encoder')
        response = self.client.get(url)
        self.assertContains(response,
                            '"timedelta": "%d:%02d"' % (NOW.hour, NOW.minute))

    def test_timedelta_seconds(self):
        self.assertEqual(timedelta_seconds(self.timedelta), 0)
        self.assertEqual(timedelta_seconds(self.timedelta001), 1)
        self.assertEqual(timedelta_seconds(self.timedelta1200), 43200)
        self.assertEqual(timedelta_seconds(self.timedelta27410), 99660)

    def test_timedelta_to_str(self):
        self.assertRaises(ValueError,
                          timedelta_to_str,
                          datetime.date.today())

        self.assertEqual(timedelta_to_str(self.timedelta), '0:00')
        self.assertEqual(timedelta_to_str(self.timedelta001), '0:00')
        self.assertEqual(timedelta_to_str(self.timedelta001, 'G:i:s'),
                         '0:00:01')
        self.assertEqual(timedelta_to_str(self.timedelta001, 'H:i:s'),
                         '00:00:01')
        self.assertEqual(timedelta_to_str(self.timedelta27410), '27:41')
        self.assertEqual(timedelta_to_str(self.timedelta274114), '27:41')
        self.assertEqual(timedelta_to_str(self.timedelta274114, 'G:i:s'),
                         '27:41:14')

        self.assertEqual(timedelta_to_str(self.timedelta7350, 'f'), '7:35:00')
        self.assertEqual(timedelta_to_str(self.timedelta73510, 'f'), '7:35:10')
        self.assertEqual(timedelta_to_str(self.timedelta24100, 'f'),
                         '1d 0:10:00')
        self.assertEqual(timedelta_to_str(self.timedelta24105, 'f'),
                         '1d 0:10:05')
        self.assertEqual(timedelta_to_str(self.timedelta27410, 'f'),
                         '1d 3:41:00')
        self.assertEqual(timedelta_to_str(self.timedelta274114, 'f'),
                         '1d 3:41:14'),
        self.assertEqual(timedelta_to_str(self.timedelta16800, 'f'),
                         '1w 0:00:00')
        self.assertEqual(timedelta_to_str(self.timedelta433280, 'f'),
                         '2w 4d 1:28:00')
        self.assertEqual(timedelta_to_str(self.timedelta433287, 'f'),
                         '2w 4d 1:28:07')

        self.assertEqual(timedelta_to_str(self.timedelta7350, 'F'), '7:35:00')
        self.assertEqual(timedelta_to_str(self.timedelta73510, 'F'), '7:35:10')
        self.assertEqual(timedelta_to_str(self.timedelta24100, 'F'),
                         '1 day, 0:10:00')
        self.assertEqual(timedelta_to_str(self.timedelta24105, 'F'),
                         '1 day, 0:10:05')
        self.assertEqual(timedelta_to_str(self.timedelta27410, 'F'),
                         '1 day, 3:41:00')
        self.assertEqual(timedelta_to_str(self.timedelta274114, 'F'),
                         '1 day, 3:41:14'),
        self.assertEqual(timedelta_to_str(self.timedelta16800, 'F'),
                         '1 week, 0:00:00')
        self.assertEqual(timedelta_to_str(self.timedelta433280, 'F'),
                         '2 weeks, 4 days, 1:28:00')
        self.assertEqual(timedelta_to_str(self.timedelta433287, 'F'),
                         '2 weeks, 4 days, 1:28:07')
