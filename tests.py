# -*- coding: utf-8 -*-

import datetime, json

import unittest

import typed

class TestTypedTest(unittest.TestCase):
	def test_int(self):
		t = typed.int
		self.assertTrue(isinstance(t, typed.IntType))

		self.assertTrue(t.test(1))
		self.assertTrue(t.test(1L))

		for value in ['a', True, [1, 2, 3], 1.2, None, {'a': 1}, self]:
			self.assertFalse(t.test(value))

	def test_date(self):
		t = typed.date
		self.assertTrue(isinstance(t, typed.DateType))

		self.assertTrue(t.test(datetime.date.today()))

		self.assertFalse(t.test(datetime.datetime.now()))

		for value in [1, 'a', True, [1, 2, 3], 1.2, None, {'a': 1}, self]:
			self.assertFalse(t.test(value))

	def test_primitive_types(self):
		primitive_types = {
				typed.float: 1.2,
				typed.none: None,
				typed.ascii: 'abc',
				typed.unicode: u'€π◊¡∞Ω√∫µß∂∆',
				typed.bool: True,
				typed.datetime: datetime.datetime.now(),
			}

		all_values = set(primitive_types.values())

		for type, value in primitive_types.items():
			self.assertTrue(isinstance(type, typed.PrimitiveType))

			self.assertTrue(type.test(value))
			for other_value in all_values - set([value]):
				self.assertFalse(type.test(other_value))

		for value in [1, [1, 2, 3], {'a': 1}, self, datetime.date.today()]:
			self.assertFalse(type.test(value))

	def test_any(self):
		t = typed.any

		for value in [1, 'a', True, [1, 2, 3], 1.2, None, {'a': 1}, self]:
			self.assertTrue(t.test(value))

	def test_string(self):
		t = typed.string
		self.assertTrue(isinstance(t, typed.PrimitiveType))

		self.assertTrue(t.test('a'))
		self.assertTrue(t.test(u'π∆µ'))

		for value in [1209, True, [1, 2, 3], 1.2, None, {'a': 1}, self]:
			self.assertFalse(t.test(value))

	def test_union(self):
		t1 = typed.string | typed.int
		self.assertTrue(isinstance(t1, typed.UnionType))
		self.assertItemsEqual(t1.types, [typed.string, typed.int])

		self.assertTrue(t1.test('a'))
		self.assertTrue(t1.test(1209))

		for value in [[1, 2, 3], 1.2, None, {'a': 1}, self]:
			self.assertFalse(t1.test(value))

		self.assertFalse(t1.test(True))
		self.assertFalse(t1.test([1, 2, 3]))
		self.assertFalse(t1.test(1.2))
		self.assertFalse(t1.test(None))

		t2 = typed.string | None
		self.assertItemsEqual(t2.types, [typed.string, typed.none])

		t3 = t1 | typed.bool
		self.assertItemsEqual(t3.types, [typed.string, typed.int, typed.bool])

		t4 = typed.none | t1
		self.assertItemsEqual(t4.types, [typed.string, typed.int, typed.none])

		t5 = t3 | t4
		self.assertItemsEqual(t5.types, [typed.string, typed.int, typed.none, typed.bool])

	def test_set(self):
		t1 = typed.set(1, 2, 3)
		self.assertTrue(isinstance(t1, typed.SetType))
		self.assertItemsEqual(t1.values, [1, 2, 3])

		self.assertTrue(t1.test(1))
		self.assertTrue(t1.test(2))
		self.assertTrue(t1.test(3))

		self.assertFalse(t1.test(4))
		self.assertFalse(t1.test(1209))
		#self.assertFalse(t1.test(True))

		for value in [[1, 2, 3], 1.2, None, {'a': 1}, self]:
			self.assertFalse(t1.test(value))

		t2 = t1 | typed.string
		self.assertTrue(isinstance(t2, typed.UnionType))
		self.assertItemsEqual(t2.types, [t1, typed.string])

		t3 = t1 | typed.set(3, None, 'a')
		self.assertTrue(isinstance(t3, typed.SetType))
		self.assertItemsEqual(t3.values, [1, 2, 3, None, 'a'])


	def test_list(self):
		self.assertRaises(TypeError, typed.list, int)

		t1 = typed.list(typed.int)
		self.assertTrue(isinstance(t1, typed.ListType))

		self.assertTrue(t1.test([1, 2, 3]))
		self.assertTrue(t1.test([]))

		self.assertFalse(t1.test([1, '2', None]))
		self.assertFalse(t1.test(tuple([1, 2, 3])))

		for value in [datetime.datetime.now(), 1, 'a', True, [1.2, 2.3, 3.4], 1.2, None, {'a': 1}, self]:
			self.assertFalse(t1.test(value))

		t2 = typed.list(typed.int | typed.string)

		self.assertTrue(t2.test([1, 'a', 2, 'b']))

		t3 = typed.list(typed.int) | typed.list(typed.string)

		self.assertFalse(t3.test([1, 'a', 2, 'b']))
		self.assertTrue(t3.test([1, 2, 3]))
		self.assertTrue(t3.test(['a', 'b', 'c']))

	def test_dict(self):
		self.assertRaises(TypeError, typed.dict, 1)
		self.assertRaises(TypeError, typed.dict, {'a', 1})
		self.assertRaises(TypeError, typed.dict, {'a', int})

		t = typed.dict({'a': typed.int, 'b': typed.bool, 'c': typed.list(typed.string)})

		self.assertTrue(t.test({'a': 1, 'b': True, 'c': ['X', 'Y']}))

		self.assertFalse(t.test({}))
		self.assertFalse(t.test({'a': 1}))
		self.assertFalse(t.test({'a': 1, 'b': True}))
		self.assertFalse(t.test({'a': 1, 'b': True, 'c': 'foo'}))
		self.assertFalse(t.test({'a': 1, 'b': True, 'c': [1, 2, 3]}))
		self.assertFalse(t.test({'a': 1, 'b': True, 'c': ['X', 'Y'], 'd': 'bar'}))


	def test_optional(self):
		t = typed.dict({'a': typed.int, 'b': typed.bool.optional, 'c': typed.list(typed.string).optional})

		self.assertTrue(t.test({'a': 1, 'b': True, 'c': ['X', 'Y']}))
		self.assertTrue(t.test({'a': 1}))
		self.assertTrue(t.test({'a': 1, 'b': True}))
		self.assertTrue(t.test({'a': 1, 'c': ['X', 'Y']}))

		self.assertFalse(t.test({}))
		self.assertFalse(t.test({'a': 1, 'b': 0.01}))
		self.assertFalse(t.test({'a': 1, 'b': True, 'c': 'foo'}))
		self.assertFalse(t.test({'a': 1, 'b': True, 'c': [1, 2, 3]}))
		self.assertFalse(t.test({'a': 1, 'b': True, 'c': ['X', 'Y'], 'd': 'bar'}))


	def test_trimmed_dict(self):
		t = typed.dict({'a': typed.int, 'b': typed.bool}).trimmed

		self.assertTrue(t.test({'a': 1, 'b': True}))
		self.assertTrue(t.test({'a': 1, 'b': True, 'c': "string"}))
		self.assertTrue(t.test({'a': 1, 'b': True, 'c': 0, 'd': 0, 'e': 0, 'f': 0}))

		self.assertFalse(t.test({}))
		self.assertFalse(t.test({'a': 1, 'b': 0.01}))
		self.assertFalse(t.test({'a': 1}))
		self.assertFalse(t.test({'a': 1, 'c': 0, 'd': 0, 'e': 0, 'f': 0}))


	def test_tuple(self):
		self.assertRaises(TypeError, typed.tuple, int, bool)

		t1 = typed.tuple(typed.int, typed.bool)

		self.assertTrue(t1.test(tuple([1, True])))
		self.assertTrue(t1.test(tuple([4, False])))

		self.assertFalse(t1.test(tuple([1])))
		self.assertFalse(t1.test(tuple([1, True, False])))
		self.assertFalse(t1.test(tuple([True, 1])))
		self.assertFalse(t1.test([1, True]))

		for value in [datetime.datetime.now(), 1, 'a', True, [1.2, 2.3, 3.4], 1.2, None, {'a': 1}, self]:
			self.assertFalse(t1.test(value))

		t2 = t1.format(typed.list)

		self.assertFalse(t2.test([1, True]))


class TestTypedLoadSave(unittest.TestCase):
	def test_simple_types(self):
		simple_types = {
				typed.int: 134,
				typed.float: 1.2,
				typed.none: None,
				typed.ascii: 'abc',
				typed.unicode: u'€π◊¡∞Ω√∫µß∂∆',
				typed.bool: True,
				typed.datetime: datetime.datetime.now(),
				typed.date: datetime.date.today(),
			}

		all_values = set(simple_types.values())

		for type, value in simple_types.items():
			self.assertEqual(type.load(value), value)
			self.assertEqual(type.save(value), value)

			for other_value in all_values - set([value]):
				self.assertRaises(ValueError, type.load, other_value)
				self.assertRaises(ValueError, type.save, other_value)

		for value in [[1, 2, 3], {'a': 1}, self]:
			self.assertRaises(ValueError, type.load, value)
			self.assertRaises(ValueError, type.save, value)

	def test_string(self):
		t = typed.string

		for value in ['abc', u'€π◊¡∞Ω√∫µß∂∆']:
			self.assertEqual(t.load(value), value)
			self.assertEqual(t.save(value), value)

		for value in [datetime.datetime.now(), 1, True, [1.2, 2.3, 3.4], 1.2, None, {'a': 1}, self]:
			self.assertRaises(ValueError, t.load, value)
			self.assertRaises(ValueError, t.save, value)

	def test_any(self):
		t = typed.any

		for value in [1, 'a', True, [1, 2, 3], 1.2, None, {'a': 1}, self]:
			self.assertEqual(t.load(value), value)
			self.assertEqual(t.save(value), value)

	def test_formatted_datetime(self):
		datetime_formats = ['%Y-%m-%dT%H:%M:%S.%f', '%Y-%m-%d %H:%M:%S', '%A, %d. %B %Y %I:%M%p']
		dt = datetime.datetime.now()

		for datetime_format in datetime_formats:
			t = typed.datetime.format(datetime_format)

			dt_str = dt.strftime(datetime_format)

			self.assertEqual(t.save(dt), dt_str, msg=datetime_format)
			self.assertEqual(t.save(t.load(dt_str)), dt_str, msg=datetime_format)

			for value in [1, 'a', True, [1, 2, 3], 1.2, None, {'a': 1}, self]:
				self.assertRaises(ValueError, t.load, value)
				self.assertRaises(ValueError, t.save, value)

	def test_union(self):
		t1 = typed.float | typed.bool | typed.none

		self.assertEqual(t1.load(0.01), 0.01)
		self.assertEqual(t1.save(0.01), 0.01)
		self.assertEqual(t1.load(False), False)
		self.assertEqual(t1.save(False), False)
		self.assertEqual(t1.load(None), None)
		self.assertEqual(t1.save(None), None)

		for value in [1, 'aerg', [1, 2, 3], {'a': 1}, self]:
			self.assertRaises(ValueError, t1.load, value)
			self.assertRaises(ValueError, t1.save, value)

		t2 = typed.num

		self.assertEqual(t2.load(0.01), 0.01)
		self.assertEqual(t2.save(0.01), 0.01)
		self.assertEqual(t2.load(1), 1)
		self.assertEqual(t2.save(1), 1)

		for value in [False, 'aerg', None, [1, 2, 3], {'a': 1}, self]:
			self.assertRaises(ValueError, t2.load, value)
			self.assertRaises(ValueError, t2.save, value)

		datetime_formats = ['%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S']
		dt = datetime.datetime(2013, 9, 21, 11, 42, 33)

		t3 = typed.datetime.format(datetime_formats[0]) | typed.datetime.format(datetime_formats[1]) | typed.int

		self.assertEqual(t3.load(1), 1)
		self.assertEqual(t3.save(1), 1)

		self.assertEqual(t3.load(dt.strftime(datetime_formats[0])), dt)
		self.assertEqual(t3.load(dt.strftime(datetime_formats[1])), dt)
		self.assertEqual(t3.save(dt), dt.strftime(datetime_formats[0]))


	def test_set(self):
		values = [1, 2, 3, 'a', None]

		t = typed.set(*values)

		for value in values:
			self.assertEqual(t.load(value), value)
			self.assertEqual(t.save(value), value)

		for value in [False, 'aerg', 4, 1234, [1, 2, 3], {'a': 1}, self]:
			self.assertRaises(ValueError, t.load, value)
			self.assertRaises(ValueError, t.save, value)

	def test_list(self):
		t1 = typed.list(typed.int)

		self.assertEqual(t1.load([1, 2, 3]), [1, 2, 3])
		self.assertEqual(t1.save([1, 2, 3]), [1, 2, 3])

		self.assertRaises(ValueError, t1.load, [1, '2', None])
		self.assertRaises(ValueError, t1.save, [1, '2', None])

		for value in [datetime.datetime.now(), 1, 'a', True, [1.2, 2.3, 3.4], 1.2, None, {'a': 1}, self]:
			self.assertRaises(ValueError, t1.load, value)
			self.assertRaises(ValueError, t1.save, value)

		t2 = typed.list(typed.int | typed.string)

		self.assertEqual(t2.load([1, 'a', 2, 'b']), [1, 'a', 2, 'b'])
		self.assertEqual(t2.save([1, 'a', 2, 'b']), [1, 'a', 2, 'b'])

		t3 = typed.list(typed.int) | typed.list(typed.string)

		self.assertRaises(ValueError, t3.load, [1, 'a', 2, 'b'])
		self.assertRaises(ValueError, t3.save, [1, 'a', 2, 'b'])

		self.assertEqual(t3.load([1, 2, 3]), [1, 2, 3])
		self.assertEqual(t3.save([1, 2, 3]), [1, 2, 3])
		self.assertEqual(t3.load(['a', 'b', 'c']), ['a', 'b', 'c'])
		self.assertEqual(t3.save(['a', 'b', 'c']), ['a', 'b', 'c'])

		datetime_format = '%Y-%m-%d %H:%M:%S'
		dt_list = [datetime.datetime(2013, 9, 21, 11, 42, 33), datetime.datetime(2012, 3, 24, 9, 6, 13)]
		dt_str_list = map(lambda dt: dt.strftime(datetime_format), dt_list)

		t4 = typed.list(typed.datetime.format(datetime_format))

		self.assertEqual(t4.load(list(dt_str_list)), dt_list)
		self.assertEqual(t4.save(list(dt_list)), dt_str_list)

	def test_dict(self):
		datetime_format = '%Y-%m-%d %H:%M:%S'
		dt = datetime.datetime(2013, 9, 21, 11, 42, 33)
		dt_str = dt.strftime(datetime_format)

		t = typed.dict({
				'a': typed.string,
				'b': typed.int.optional,
				'c': typed.bool.default(False),
				'd': typed.set(0, 1).default(0),
				'e': typed.datetime.format(datetime_format).optional,
				'f': typed.optional,
				'g': typed.default(None),
				'h': (typed.int | typed.none).default(None)
			})

		self.assertEqual(t.load({'a': ''}), {'a': '', 'c': False, 'd': 0, 'g': None, 'h': None})
		self.assertEqual(t.load({'a': '', 'f': 1, 'g': 'foo'}), {'a': '', 'c': False, 'd': 0, 'f': 1, 'g': 'foo', 'h': None})
		self.assertEqual(t.load({'a': '', 'f': True, 'g': [1, 2, 3]}), {'a': '', 'c': False, 'd': 0, 'f': True, 'g': [1, 2, 3], 'h': None})
		self.assertEqual(t.load({'a': '', 'b': 2, 'c': True, 'd': 1}), {'a': '', 'b': 2, 'c': True, 'd': 1, 'g': None, 'h': None})
		self.assertEqual(t.load({'a': '', 'e': dt_str, 'h': 1}), {'a': '', 'c': False, 'd': 0, 'e': dt, 'g': None, 'h': 1})
		self.assertEqual(t.load({'a': '', 'h': None}), {'a': '', 'c': False, 'd': 0, 'g': None, 'h': None})

		self.assertEqual(t.save({'a': ''}), {'a': ''})
		self.assertEqual(t.save({'a': '', 'd': 0, 'h': None}), {'a': ''})
		self.assertEqual(t.save({'a': '', 'c': False, 'd': 0, 'g': None, 'h': None}), {'a': ''})
		self.assertEqual(t.save({'a': '', 'c': False, 'd': 0, 'f': 1, 'g': [1, 2, 3], 'h': None}), {'a': '', 'f': 1, 'g': [1, 2, 3]})
		self.assertEqual(t.save({'a': '', 'c': False, 'd': 0, 'f': True, 'g': None, 'h': None}), {'a': '', 'f': True})
		self.assertEqual(t.save({'a': '', 'b': 2, 'c': True, 'd': 1, 'g': None, 'h': None}), {'a': '', 'b': 2, 'c': True, 'd': 1})
		self.assertEqual(t.save({'a': '', 'c': False, 'd': 0, 'e': dt, 'g': None, 'h': 1}), {'a': '', 'e': dt_str, 'h': 1})

		self.assertRaises(ValueError, t.load, {})
		self.assertRaises(ValueError, t.load, {'a': '', 'b': 'foo'})
		self.assertRaises(ValueError, t.load, {'a': '', 'd': 2})
		self.assertRaises(ValueError, t.load, {'a': '', 'e': '2012-12-12T12:12:12'})
		self.assertRaises(ValueError, t.load, {'a': '', 'h': 'foo'})

		self.assertRaises(ValueError, t.save, {})
		self.assertRaises(ValueError, t.save, {'a': '', 'b': 'foo'})
		self.assertRaises(ValueError, t.save, {'a': '', 'd': 2})
		self.assertRaises(ValueError, t.save, {'a': '', 'e': '2012-12-12T12:12:12'})
		self.assertRaises(ValueError, t.save, {'a': '', 'h': 'foo'})
		self.assertRaises(ValueError, t.save, {'a': '', 'c': False, 'd': 0, 'g': None, 'h': 1, 't': 0, 'u': 0, 'v': 0})

	def test_trimmed_dict(self):
		t = typed.dict({
				'a': typed.string,
				'b': typed.int.optional,
				'c': typed.bool.default(False)
			}).trimmed


		self.assertEqual(t.load({'a': ''}), {'a': '', 'c': False})
		self.assertEqual(t.load({'a': '', 'b': 2}), {'a': '', 'b': 2, 'c': False})
		self.assertEqual(t.load({'a': '', 'c': True}), {'a': '', 'c': True})
		self.assertEqual(t.load({'a': '', 'b': 2, 'c': True}), {'a': '', 'b': 2, 'c': True})

		self.assertEqual(t.load({'a': '', 'd': 1, 'e': 0}), {'a': '', 'c': False})
		self.assertEqual(t.load({'a': '', 'b': 2, 'd': 1, 'e': 0, 'f': -1}), {'a': '', 'b': 2, 'c': False})
		self.assertEqual(t.load({'a': '', 'c': True, 'd': 1, 'e': 0, 'f': -1}), {'a': '', 'c': True})
		self.assertEqual(t.load({'a': '', 'b': 2, 'c': True, 'd': 1, 'e': 0, 'f': -1}), {'a': '', 'b': 2, 'c': True})

		self.assertEqual(t.save({'a': ''}), {'a': ''})
		self.assertEqual(t.save({'a': '', 'c': False}), {'a': ''})
		self.assertEqual(t.save({'a': '', 'c': True}), {'a': '', 'c': True})
		self.assertEqual(t.save({'a': '', 'b': 2}), {'a': '', 'b': 2})
		self.assertEqual(t.save({'a': '', 'b': 2, 'c': True}), {'a': '', 'b': 2, 'c': True})

		self.assertEqual(t.save({'a': '', 'd': 1, 'e': 0}), {'a': ''})
		self.assertEqual(t.save({'a': '', 'c': False, 'd': 1, 'e': 0, 'f': -1}), {'a': ''})
		self.assertEqual(t.save({'a': '', 'b': 2, 'd': 1, 'e': 0, 'f': -1}), {'a': '', 'b': 2})
		self.assertEqual(t.save({'a': '', 'b': 2, 'c': False, 'd': 1, 'e': 0, 'f': -1}), {'a': '', 'b': 2})
		self.assertEqual(t.save({'a': '', 'b': 2, 'c': True, 'd': 1, 'e': 0, 'f': -1}), {'a': '', 'b': 2, 'c': True})

		self.assertRaises(ValueError, t.load, {})
		self.assertRaises(ValueError, t.load, {'a': '', 'b': 'foo'})
		self.assertRaises(ValueError, t.load, {'a': '', 'c': 2})


	def test_format_datetime(self):
		datetime_formats = ['%Y-%m-%dT%H:%M:%S.%f', '%Y-%m-%d %H:%M:%S', '%A, %d. %B %Y %I:%M%p']
		dt = datetime.datetime.now()

		for datetime_format in datetime_formats:
			t = typed.datetime.format(datetime_format)

			self.assertTrue(t.test(dt))

			dt_str = dt.strftime(datetime_format)
			new_dt = datetime.datetime.strptime(dt_str, datetime_format)

			self.assertEqual(t.save(dt), dt_str)
			self.assertEqual(t.load(dt_str), new_dt)


	def test_format_date(self):
		datetime_formats = ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%A, %d. %B %Y %I:%M%p']
		dt = datetime.date.today()

		for datetime_format in datetime_formats:
			t = typed.date.format(datetime_format)

			self.assertTrue(t.test(dt))

			dt_str = dt.strftime(datetime_format)
			new_dt = datetime.datetime.strptime(dt_str, datetime_format).date()

			self.assertEqual(t.save(dt), dt_str)
			self.assertEqual(t.load(dt_str), new_dt)


	def test_format_dict(self):
		t1 = typed.dict({
				'a': typed.int.format({1: 'one', 2: 'two'}),
				'b': typed.bool.format({True: 1, False: 0}),
			})

		self.assertEqual(t1.load({'a': 1, 'b': True}), {'a': 1, 'b': True})
		self.assertEqual(t1.load({'a': 'one', 'b': 1}), {'a': 1, 'b': True})
		self.assertEqual(t1.load({'a': 'two', 'b': 0}), {'a': 2, 'b': False})
		self.assertEqual(t1.load({'a': 3, 'b': True}), {'a': 3, 'b': True})

		self.assertEqual(t1.save({'a': 1, 'b': True}), {'a': 'one', 'b': 1})
		self.assertEqual(t1.save({'a': 2, 'b': False}), {'a': 'two', 'b': 0})
		self.assertEqual(t1.save({'a': 3, 'b': True}), {'a': 3, 'b': 1})

		self.assertRaises(ValueError, t1.load, {'a': 'three'})

		t2 = (typed.int | typed.null).format({1: 'one', None: 'nothing'})

		self.assertEqual(t2.load('one'), 1)
		self.assertEqual(t2.load(1), 1)
		self.assertEqual(t2.load(2), 2)
		self.assertEqual(t2.load('nothing'), None)

		self.assertEqual(t2.save(1), 'one')
		self.assertEqual(t2.save(None), 'nothing')
		self.assertEqual(t2.save(2), 2)

		t3 = typed.bool.format({True: 1, False: 0}) | typed.int.format({0: 'zero', 1: 'one'})

		self.assertEqual(t3.load('one'), 1)
		self.assertEqual(t3.load('zero'), 0)
		self.assertEqual(t3.load(3), 3)
		self.assertEqual(t3.load(0), False)
		self.assertEqual(t3.load(1), True)

		self.assertEqual(t3.save(1), 'one')
		self.assertEqual(t3.save(2), 2)
		self.assertEqual(t3.save(0), 'zero')
		self.assertEqual(t3.save(False), 0)
		self.assertEqual(t3.save(True), 1)

		t4 = typed.dict({
				'a': typed.int.optional.format({1: 'one', 2: 'two'}),
				'b': typed.bool.default(False).format({False: 'wrong', True: 'right'}),
				'c': typed.float.format({1.0: '100%', 0.0: '0%'}).default(0.0),
				'd': (typed.bool | typed.none).format({None: 'nothing'}).optional,
				'e': typed.datetime.format('%Y-%m-%d %H:%M:%S').format({'1970-01-01 00:00:00': 'forever'}).optional,
			})

		self.assertEqual(t4.load({}), {'b': False, 'c': 0.0})
		self.assertEqual(t4.load({'a': 3, 'b': True, 'c': 0.5, 'd': None, 'e': '2013-10-11 11:02:45'}), {'a': 3, 'b': True, 'c': 0.5, 'd': None, 'e': datetime.datetime(2013, 10, 11, 11, 02, 45)})
		self.assertEqual(t4.load({'a': 'one', 'b': 'right', 'c': '0%', 'd': 'nothing', 'e': 'forever'}), {'a': 1, 'b': True, 'c': 0.0, 'd': None, 'e': datetime.datetime(1970, 01, 01, 00, 00, 00)})

		self.assertEqual(t4.save({}), {})
		self.assertEqual(t4.save({'a': 2, 'b': True, 'c': 1.0, 'd': True, 'e': datetime.datetime(2014, 12, 15, 16, 10, 32)}), {'a': 'two', 'b': 'right', 'c': '100%', 'd': True, 'e': '2014-12-15 16:10:32'})
		self.assertEqual(t4.save({'a': 3, 'b': False, 'c': 0.0, 'd': None, 'e': datetime.datetime(1970, 01, 01, 00, 00, 00)}), {'a': 3, 'd': 'nothing', 'e': 'forever'})


	def test_format_json(self):
		t1 = typed.dict({
				'a': typed.datetime.format('%Y-%m-%d %H:%M:%S').optional,
				'b': (typed.string | typed.none).optional,
				'c': typed.bool.format({True: 1, False: 0}).default(False),
			})

		t2 = typed.dict({
				'd': typed.int,
				'e': (typed.none | typed.date.format('%d/%m/%Y')).default(None),
				'f': typed.list(typed.int),
				'g': typed.json(t1).default(t1.load({})),
			}).format(typed.json)

		self.assertEqual(t2.load(json.dumps({'d': 1, 'f': []})), {'d': 1, 'e': None, 'f': [], 'g': {'c': False}})
		self.assertEqual(t2.load(json.dumps({'d': 0, 'e': None, 'f': [1, 2], 'g': json.dumps({'b': None, 'c': 1})})), {'d': 0, 'e': None, 'f': [1, 2], 'g': {'b': None, 'c': True}})
		self.assertEqual(t2.load(json.dumps({'d': 1, 'e': '15/02/2011', 'f': [], 'g': json.dumps({'a': '2013-11-11 16:16:16', 'b': 'foo', 'c': 0})})), {'d': 1, 'e': datetime.date(2011, 02, 15), 'f': [], 'g': {'a': datetime.datetime(2013, 11, 11, 16, 16, 16), 'b': 'foo', 'c': False}})

		self.assertEqual(t2.save({'d': 1, 'f': [1, 2, 3, 4]}), json.dumps({'d': 1, 'f': [1, 2, 3, 4]}))
		self.assertEqual(t2.save({'d': 1, 'e': None, 'f': [1, 2, 3, 4], 'g': {'c': False}}), json.dumps({'d': 1, 'f': [1, 2, 3, 4]}))
		self.assertEqual(t2.save({'d': 1, 'e': datetime.date(2013, 02, 15), 'f': [], 'g': {'a': datetime.datetime(2013, 10, 10, 05, 55, 50), 'b': None, 'c': True}}), json.dumps({'d': 1, 'e': '15/02/2013', 'f': [], 'g': json.dumps({'a': '2013-10-10 05:55:50', 'b': None, 'c': 1})}))


	def test_tuple(self):
		t1 = typed.tuple(typed.int, typed.datetime.format('%Y-%m-%d %H:%M:%S'), typed.string | typed.none)

		self.assertEqual(t1.load(tuple([4, '2013-10-11 11:02:45', 'foo'])), (4, datetime.datetime(2013, 10, 11, 11, 02, 45), 'foo'))
		self.assertEqual(t1.load(tuple([4, '2013-10-11 11:02:45', None])), (4, datetime.datetime(2013, 10, 11, 11, 02, 45), None))

		self.assertRaises(ValueError, t1.load, tuple([4, '2013-10-11 11:02:45']))
		self.assertRaises(ValueError, t1.load, tuple([4, '2013-10-11T11:02:45', 'foo']))
		self.assertRaises(ValueError, t1.load, tuple([True, '2013-10-11 11:02:45', 'foo']))
		self.assertRaises(ValueError, t1.load, tuple([3, '2013-10-11 11:02:45', 'foo', None]))
		self.assertRaises(ValueError, t1.load, [3, '2013-10-11 11:02:45', None])

		self.assertEqual(t1.save(tuple([4, datetime.datetime(2013, 10, 11, 11, 02, 45), None])), (4, '2013-10-11 11:02:45', None))
		self.assertEqual(t1.save(tuple([0, datetime.datetime(2013, 10, 11, 11, 02, 45), 'foo'])), (0, '2013-10-11 11:02:45', 'foo'))

		self.assertRaises(ValueError, t1.save, tuple([4, datetime.datetime(2013, 10, 11, 11, 02, 45)]))
		self.assertRaises(ValueError, t1.save, tuple([True, datetime.datetime(2013, 10, 11, 11, 02, 45), 'foo']))
		self.assertRaises(ValueError, t1.save, tuple([3, datetime.datetime(2013, 10, 11, 11, 02, 45), 'foo', None]))
		self.assertRaises(ValueError, t1.save, [3, datetime.datetime(2013, 10, 11, 11, 02, 45), None])

		t2 = t1.format(typed.list)

		self.assertEqual(t2.load([4, '2013-10-11 11:02:45', None]), (4, datetime.datetime(2013, 10, 11, 11, 02, 45), None))

		self.assertRaises(ValueError, t2.load, tuple([4, '2013-10-11 11:02:45', None]))
		self.assertRaises(ValueError, t2.load, 1)

		self.assertEqual(t2.save(tuple([4, datetime.datetime(2013, 10, 11, 11, 02, 45), None])), [4, '2013-10-11 11:02:45', None])
		self.assertEqual(t2.save(tuple([0, datetime.datetime(2013, 10, 11, 11, 02, 45), 'foo'])), [0, '2013-10-11 11:02:45', 'foo'])

		self.assertRaises(ValueError, t2.save, [3, datetime.datetime(2013, 10, 11, 11, 02, 45), None])
















if __name__ == '__main__':
    unittest.main()
