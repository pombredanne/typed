import numbers, types, datetime

class O(object):
	pass

python = O()
python.type = type
python.int = int
python.str = str
python.unicode = unicode
python.float = float
python.bool = bool
python.long = long
python.set = set
python.frozenset = frozenset
python.datetime = datetime
python.list = list
python.dict = dict
python.any = any


class Type(object):
	__slots__ = []

	def __init__(self):
		raise Exception('abstract')

	def test(self, obj):
		raise NotImplementedError()

	def make_optional(self):
		return OptionalType(self)

	optional = property(make_optional)

	def default(self, value):
		return DefaultType(self, value)

	def load(self, obj):
		if not self.test(obj):
			raise ValueError('object has invalid type')

		return obj

	def save(self, obj):
		if not self.test(obj):
			raise ValueError('object has invalid type')

		return obj

	def __or__(self, another_type):
		if another_type is None:
			return UnionType(self, none)
		elif isinstance(another_type, UnionType):
			return UnionType(self, *another_type.types)
		elif isinstance(another_type, Type):
			return UnionType(self, another_type)
		else:
			return NotImplemented


class AnyType(Type):
	__slots__ = []

	def __init__(self):
		pass

	def test(self, obj):
		return True

	def load(self, obj):
		return obj

	def save(self, obj):
		return obj


class PrimitiveType(Type):
	__slots__ = ['type']

	def __init__(self, t):
		self.type = t

	def test(self, obj):
		return isinstance(obj, self.type)

class IntType(Type):
	__slots__ = []
	def __init__(self):
		pass

	def test(self, obj):
		return isinstance(obj, (python.int, python.long)) and not isinstance(obj, python.bool)


class UnionType(Type):
	__slots__ = ['types']

	def __init__(self, *args):
		if len(args) == 1 and not isinstance(args[0], Type):
			args = args[0]
		self.types = args

	def test(self, obj):
		return python.any(t.test(obj) for t in self.types)

	def __or__(self, another_type):
		if another_type is None:
			return UnionType(none, *self.types)
		elif isinstance(another_type, UnionType):
			return UnionType(python.frozenset(self.types + another_type.types))
		else:
			return UnionType(another_type, *self.types)

	def load(self, obj):
		for type in self.types:
			try:
				return type.load(obj)
			except ValueError:
				continue

		raise ValueError('object matches none of the valid types')
		
	def save(self, obj):
		for type in self.types:
			try:
				return type.save(obj)
			except ValueError:
				continue

		raise ValueError('object matches none of the valid types')


class SetType(Type):
	__slots__ = ['values']

	def __init__(self, values):
		if not isinstance(values, python.frozenset):
			values = python.frozenset(values)
		self.values = values

	def test(self, obj):
		try:
			return obj in self.values
		except TypeError:		# unhashable types
			return False

	def __or__(self, another_type):
		if isinstance(another_type, SetType):
			return SetType(self.values | another_type.values)
		else:
			return super(SetType, self).__or__(another_type)


class DateType(Type):
	__slots__ = []
	def __init__(self):
		pass

	def test(self, obj):
		return isinstance(obj, python.datetime.date) and not isinstance(obj, python.datetime.datetime)


class DatetimeType(PrimitiveType):
	def __init__(self):
		super(DatetimeType, self).__init__(datetime.datetime)

	def format(self, fmt):
		return FormattedDatetimeType(fmt)


class FormattedDatetimeType(Type):
	__slots__ = ['format']

	def __init__(self, fmt):
		self.format = fmt

	def test(self, obj):
		if not isinstance(obj, basestring):
			return False
		try:
			python.datetime.datetime.strptime(obj, self.format)
			return True
		except ValueError:
			return False

	def load(self, obj):
		if not isinstance(obj, basestring):
			raise ValueError('object is not a string')

		try:
			return python.datetime.datetime.strptime(obj, self.format)
		except TypeError, e:
			raise ValueError(e.message)

	def save(self, obj):
		if not isinstance(obj, python.datetime.datetime):
			raise ValueError('object is not a datetime')

		return obj.strftime(self.format)


class ListType(Type):
	__slots__ = ['type']

	def __init__(self, type):
		self.type = type

	def test(self, obj):
		if not isinstance(obj, python.list):
			return False

		t = self.type
		return all(t.test(el) for el in obj)

	def load(self, obj):
		if not isinstance(obj, python.list):
			raise ValueError('object is not a list')

		t = self.type
		for i in range(len(obj)):
			obj[i] = t.load(obj[i])

		return obj

	def save(self, obj):
		if not isinstance(obj, python.list):
			raise ValueError('object is not a list')

		t = self.type
		for i in range(len(obj)):
			obj[i] = t.save(obj[i])

		return obj


class DictType(Type):
	__slots__ = ['fields']

	def __init__(self, fields_dict):
		self.fields = frozenset(fields_dict.iteritems())

	def test(self, obj):
		if not isinstance(obj, python.dict):
			return False

		num = 0
		for field, type in self.fields:
			try:
				value = obj[field]
			except KeyError:
				if isinstance(type, OptionalType):
					continue
				return False

			if not type.test(value):
				return False
			num += 1

		if len(obj) > num:
			return False

		return True

	def load(self, obj):
		if not isinstance(obj, python.dict):
			raise ValueError('object is not a dict')

		num = 0
		for field, type in self.fields:
			try:
				value = obj[field]
			except KeyError:
				if isinstance(type, DefaultType):
					obj[field] = type.default_value
					num += 1
					continue
				if isinstance(type, OptionalType):
					continue
				raise ValueError('dict is missing field %s' % repr(field))

			obj[field] = type.load(value)
			num += 1

		if len(obj) > num:
			raise ValueError('dict has unexpected fields')

		return obj

	def save(self, obj):
		if not isinstance(obj, python.dict):
			raise ValueError('object is not a dict')

		num = 0
		for field, type in self.fields:
			try:
				value = obj[field]
			except KeyError:
				if isinstance(type, OptionalType):
					continue
				raise ValueError('dict is missing field %s' % repr(field))

			num += 1

			if isinstance(type, DefaultType) and value == type.default_value:
				del obj[field]
				continue

			obj[field] = type.save(value)

		if len(obj) > num:
			raise ValueError('dict has additional fields')

		return obj


class OptionalType(Type):
	__slots__ = ['type']

	def __init__(self, type):
		self.type = type

	def test(self, obj):
		return self.type.test(obj)

	def load(self, obj):
		return self.type.load(obj)

	def save(self, obj):
		return self.type.save(obj)


class DefaultType(OptionalType):
	__slots__ = ['default_value']

	def __init__(self, type, default_value):
		self.type = type
		self.default_value = default_value




int = integer = IntType()
float = PrimitiveType(python.float)
null = none = PrimitiveType(types.NoneType)
ascii = str = PrimitiveType(python.str)
unicode = PrimitiveType(python.unicode)
string = PrimitiveType(basestring)
bool = boolean = PrimitiveType(python.bool)
date = DateType()
datetime = DatetimeType()


def set(*values):
	return SetType(values)

number = num = int | float

def list(type):
	if not isinstance(type, Type):
		raise TypeError('typed.list() argument must be a typed type')

	return ListType(type)

def dict(fields_dict):
	if not isinstance(fields_dict, python.dict):
		raise TypeError('typed.dict() argument must be a python dict')
	if not all(isinstance(field_type, Type) for field_type in fields_dict.itervalues()):
		raise TypeError('typed.dict() argument must have values which are typed types')

	return DictType(fields_dict)

any = AnyType()
optional = any.optional

def default(value):
	return any.default(value)
