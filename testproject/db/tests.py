# -*- coding: utf-8 -*-

import datetime

from random import randint

from django.contrib.auth.models import User
from django.test import TestCase

from testproject.db.models import DummyObject, JSONModel, MonthModel, \
    PickleModel, TimeDeltaModel


USERNAME = 'test_username'
PASSWORD = 'test_password'
EMAIL = 'test_email@domain.com'

TEST_TIMES = {
    'blank': (
        ('72:00', datetime.timedelta(seconds=259200)),
        ('1 day, 11:39:00', datetime.timedelta(seconds=128340)),
        ('2 days, 1:11:00', datetime.timedelta(seconds=177060)),
        (datetime.timedelta(hours=72, minutes=30),
         datetime.timedelta(seconds=261000)),
        (129600, datetime.timedelta(seconds=129600)),
    ),
    'filled': (
        (('72:00', '72:00'), (datetime.timedelta(seconds=259200),
                              datetime.timedelta(seconds=259200))),
        (('1 day, 11:39:00', '1 day, 11:39:00'),
         (datetime.timedelta(seconds=128340),
          datetime.timedelta(seconds=128340))),
        (('2 days, 1:11:00', '2 days, 1:11:00'),
         (datetime.timedelta(seconds=177060),
          datetime.timedelta(seconds=177060))),
        ((datetime.timedelta(hours=72, minutes=30),
          datetime.timedelta(hours=72, minutes=30)),
         (datetime.timedelta(seconds=261000),
          datetime.timedelta(seconds=261000))),
        ((129600, 129600), (datetime.timedelta(seconds=129600),
                            datetime.timedelta(seconds=129600))),
    ),
}

TODAY = datetime.date.today


class TestJSONField(TestCase):

    def check(self, field, value, create=False, delete=False, exists=None):
        field = '%s_field' % field
        klass = JSONModel
        lookup = {field: value}

        if create:
            klass.objects.create(**lookup)
        elif exists:
            for key, val in lookup.items():
                setattr(exists, key, val)
            exists.save()
        else:
            assert False, 'Please, create new "JSONModel" object or ' \
                          'call "check" with "exists" keyword argument.'

        obj = klass.objects.get(**lookup)
        self.assertEqual(getattr(obj, field), value)

        if delete:
            obj.delete()
            return True

        return obj

    def test_bool_value(self):
        first, second = True, False

        obj = self.check('bool', first, create=True)
        self.check('bool', second, exists=obj, delete=True)

    def test_default_values(self):
        obj = JSONModel.objects.create()

        self.assertTrue(obj.bool_field)
        self.assertEqual(obj.dict_field, {})
        self.assertEqual(obj.float_field, 0.0)
        self.assertEqual(obj.int_field, 0)
        self.assertEqual(obj.list_field, [])
        self.assertEqual(obj.str_field, '')
        self.assertEqual(obj.unicode_field, u'')

        obj.delete()

    def test_dict_value(self):
        first, second = {'a': 1, 'b': 2, 'c': 3}, {'z': 26, 'y': 25, 'x': 24}

        obj = self.check('dict', first, create=True)
        self.check('dict', second, exists=obj, delete=True)

    def test_float_value(self):
        first, second, third = -1.5, 0.0, 1.5

        obj = self.check('float', first, create=True)
        obj = self.check('float', second, exists=obj)
        self.check('float', third, exists=obj, delete=True)

    def test_int_value(self):
        first, second, third = -1, 0, 1

        obj = self.check('int', first, create=True)
        obj = self.check('int', second, exists=obj)
        self.check('int', third, exists=obj, delete=True)

    def test_list_value(self):
        first, second = [1, 2, 3, 'a', 'b', 'c'], [26, 25, 24, 'z', 'y', 'x']

        obj = self.check('list', first, create=True)
        self.check('list', second, exists=obj, delete=True)

    def test_str_value(self):
        first, second = 'first', 'second'

        obj = self.check('str', first, create=True)
        self.check('str', second, exists=obj, delete=True)

    def test_unicode_value(self):
        first, second = u'первый', u'второй'

        obj = self.check('unicode', first, create=True)
        self.check('unicode', second, exists=obj, delete=True)


class TestMonthField(TestCase):

    def setUp(self):
        self.today = TODAY()

    def test_blank_values(self):
        self.assertRaises(Exception,
                          MonthModel.objects.create)

        obj = MonthModel.objects.create(first_month=self.today)

        first_day = self.today - datetime.timedelta(days=self.today.day - 1)

        self.assertEqual(obj.default_month, first_day)
        self.assertEqual(obj.first_month, first_day)
        self.assertEqual(obj.last_month, None)

        MonthModel.objects.get(default_month=self.today)
        MonthModel.objects.get(first_month=self.today)
        obj = MonthModel.objects.get(last_month=None)

        self.assertEqual(obj.default_month, first_day)
        self.assertEqual(obj.first_month, first_day)
        self.assertEqual(obj.last_month, None)

        obj.delete()

    def test_filled_values(self):
        default_month_delta = datetime.timedelta(weeks=randint(1, 12) * 4)
        first_month_delta = datetime.timedelta(weeks=randint(1, 6) * 4)
        last_month_delta = datetime.timedelta(weeks=randint(1, 6) * 4)

        default_month = self.today - default_month_delta
        first_month = self.today - first_month_delta
        last_month = self.today + last_month_delta

        day = datetime.timedelta(days=1)

        default_day = default_month - \
            datetime.timedelta(days=default_month.day - 1)
        first_day = first_month - datetime.timedelta(days=first_month.day - 1)
        last_day = last_month - datetime.timedelta(days=last_month.day - 1)

        obj = MonthModel.objects.create(default_month=default_month,
                                        first_month=first_month,
                                        last_month=last_month)

        self.assertEqual(obj.default_month, default_day)
        self.assertEqual(obj.first_month, first_day)
        self.assertEqual(obj.last_month, last_day)

        MonthModel.objects.get(default_month=default_month)
        MonthModel.objects.get(first_month=first_month)
        obj = MonthModel.objects.get(last_month=last_month)

        self.assertEqual(obj.default_month, default_day)
        self.assertEqual(obj.first_month, first_day)
        self.assertEqual(obj.last_month, last_day)

        obj.delete()


class TestPickleField(TestCase):

    def check(self, field, value, create=False, delete=False, exists=None):
        field = '%s_field' % field
        klass = PickleModel
        lookup = {field: value}

        if create:
            klass.objects.create(**lookup)
        elif exists:
            for key, val in lookup.items():
                setattr(exists, key, val)
            exists.save()
        else:
            assert False, 'Please, create new "PickleModel" object or ' \
                          'call "check" with "exists" keyword argument.'

        obj = klass.objects.get(**lookup)
        self.assertEqual(getattr(obj, field), value)

        if delete:
            obj.delete()
            return True

        return obj

    def test_bool_value(self):
        first, second = True, False

        obj = self.check('bool', first, create=True)
        self.check('bool', second, exists=obj, delete=True)

    def test_default_values(self):
        obj = PickleModel.objects.create()

        self.assertTrue(obj.bool_field)
        self.assertEqual(obj.dict_field, {})
        self.assertEqual(obj.float_field, 0.0)
        self.assertEqual(obj.int_field, 0)
        self.assertEqual(obj.list_field, [])
        self.assertEqual(obj.long_field, 0L)
        self.assertEqual(obj.object_field, DummyObject())
        self.assertEqual(obj.str_field, '')
        self.assertEqual(obj.tuple_field, tuple())
        self.assertEqual(obj.unicode_field, u'')

        obj.delete()

    def test_dict_value(self):
        first, second = {'a': 1, 'b': 2, 'c': 3}, {'z': 26, 'y': 25, 'x': 24}

        obj = self.check('dict', first, create=True)
        self.check('dict', second, exists=obj, delete=True)

    def test_dummy_object(self):
        self.assertEqual(DummyObject(), DummyObject())

    def test_float_value(self):
        first, second, third = -1.5, 0.0, 1.5

        obj = self.check('float', first, create=True)
        obj = self.check('float', second, exists=obj)
        self.check('float', third, exists=obj, delete=True)

    def test_int_value(self):
        first, second, third = -1, 0, 1

        obj = self.check('int', first, create=True)
        obj = self.check('int', second, exists=obj)
        self.check('int', third, exists=obj, delete=True)

    def test_list_value(self):
        first, second = [1, 2, 3, 'a', 'b', 'c'], [26, 25, 24, 'z', 'y', 'x']

        obj = self.check('list', first, create=True)
        self.check('list', second, exists=obj, delete=True)

    def test_long_value(self):
        first, second, third = -1L, 0L, 1L

        obj = self.check('long', first, create=True)
        obj = self.check('long', second, exists=obj)
        self.check('long', third, exists=obj, delete=True)

    def test_object_value(self):
        first = DummyObject()
        second = User.objects.create_user(username=USERNAME,
                                          password=PASSWORD,
                                          email=EMAIL)
        third = JSONModel.objects.create()

        obj = self.check('object', first, create=True)
        obj = self.check('object', second, exists=obj)
        obj = self.check('object', third, exists=obj)

        # Make sure that Django model does not convert to PK after model
        # update
        obj.save()
        obj = PickleModel.objects.get()

        self.assertEqual(obj.object_field, third)
        obj.delete()

        # Create new model instance with Django model
        obj = PickleModel.objects.create(object_field=third)

        # Again check that Django model does not convert to PK after model
        # update
        obj.bool_field = False
        obj.save()

        # Read object from database
        obj = PickleModel.objects.get(object_field=third)
        obj.delete()

    def test_str_value(self):
        first, second = 'first', 'second'

        obj = self.check('str', first, create=True)
        self.check('str', second, exists=obj, delete=True)

    def test_tuple_value(self):
        first, second = (1, 2, 3, 'a', 'b', 'c'), (26, 25, 24, 'z', 'y', 'x')

        obj = self.check('tuple', first, create=True)
        self.check('tuple', second, exists=obj, delete=True)

    def test_unicode_value(self):
        first, second = u'первый', u'второй'

        obj = self.check('unicode', first, create=True)
        self.check('unicode', second, exists=obj, delete=True)


class TestTimeDeltaField(TestCase):

    def test_blank_values(self):
        for time, check in TEST_TIMES['blank']:
            obj = TimeDeltaModel.objects.create(total_time=time)
            self.assertEqual(obj.total_time, check)
            self.assertEqual(obj.average_total_time, None)

        for time, check in TEST_TIMES['blank']:
            obj = TimeDeltaModel.objects.get(total_time=time)
            self.assertEqual(obj.total_time, check)
            self.assertEqual(obj.average_total_time, None)

    def test_error_value(self):
        obj = TimeDeltaModel()

        self.assertRaises(AssertionError,
                          setattr, obj, 'total_time', '')
        self.assertRaises(AssertionError,
                          setattr, obj, 'total_time', '123456789')
        self.assertRaises(AssertionError,
                          setattr, obj, 'total_time', 1234567.89)

    def test_filled_values(self):
        for times, checks in TEST_TIMES['filled']:
            obj = TimeDeltaModel.objects.create(total_time=times[0],
                                                average_total_time=times[1])
            self.assertEqual(obj.total_time, checks[0])
            self.assertEqual(obj.average_total_time, checks[1])

        for times, checks in TEST_TIMES['filled']:
            obj = TimeDeltaModel.objects.get(total_time=times[0],
                                             average_total_time=times[1])
            self.assertEqual(obj.total_time, checks[0])
            self.assertEqual(obj.average_total_time, checks[1])
