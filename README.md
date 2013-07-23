Typed - a Python type and data validation library
========================================

Tired of writing your own dataserialization routines? Want to quickly check that the inputs have the expected types? Wish you could easily reduce the space consumption of your data dumps?

Then `typed` might be for you. The `typed` library helps you describe your datatypes very quickly and clearly, and can be used for data validation, as well as for loading and saving data using custom serialization formats.


Quickstart
----------

Import the library:

```python
import typed
```

Simple type-checking:

```python
t1 = typed.int | typed.string | typed.none
t2 = typed.set(1,2,3) | typed.float | typed.list(typed.string)
t3 = typed.tuple(typed.int, typed.string) | typed.bool

assert all([
		t1.test(1), t1.test('abc'), t1.test(u'foo'), t1.test(None), not t1.test(False),
		t2.test(2), not t2.test(4), t2.test(4.0), t2.test(['a', 'b', 'c']),
		t3.test(True), t3.test((1, 'bar'))
	])
```

Data dumping:

```python
t = typed.dict({
		'name': typed.string,
		'score': typed.float.optional,
		'active': typed.bool.default(True),
		'category': (typed.set('a', 'b', 'c') | typed.none).default(None),
	}).trimmed

d = {
		'name': 'Raptor',
		#'score': 100.0,
		'active': True,
		'category': 'c',
		'url': 'https://en.wikipedia.org/wiki/Velociraptor',
	}

t.save(d)

assert d == {
		'name': 'Raptor',
		'category': 'c',
	}
```

Translating between different storage formats:

```python
t_load = typed.dict({
		'id': typed.int,
		'last_modified': typed.datetime.format('%Y-%m-%d %H:%M:%S'),
		'visibility': typed.bool.format({True: '1', False: '0'}),
		'properties': typed.json(typed.dict({
				'title': typed.string.default(''),
				'body': typed.string.default(''),
				'tags': typed.list(typed.string).default([]),
			})).format({'{}': ''}),
	}).format(typed.json)

properties_t = typed.dict({
				'title': typed.string.default(''),
				'body': typed.string.default(''),
				'tags': typed.list(typed.string).default([]),
			})

t_save = typed.dict({
		'id': typed.int,
		'last_modified': typed.datetime.format('%Y-%m-%dT%H:%M:%S'),
		'visibility': typed.bool.format({False: 'hidden'}).default(True),
		'properties': properties_t.default(properties_t.load({})),
	})

data_json = r'''{"id": 1, "last_modified": "2012-04-15 16:02:34", "visibility": "0", "properties": ""}'''

data = t_load.load(data_json)
#process data
data = t_save.save(data)

assert data == {'id': 1, 'last_modified': '2012-04-15T16:02:34', 'visibility': 'hidden'}

data_json = r'''{"id": 2, "last_modified": "2013-06-27 03:16:32", "visibility": "1", "properties": "{\"title\": \"First Post\", \"tags\": [\"life\", \"events\"]}"}'''

data = t_load.load(data_json)
#process data
data = t_save.save(data)

assert data == {'id': 2, 'last_modified': '2013-06-27T03:16:32', 'properties': {'title': 'First Post', 'tags': ['life', 'events']}}
```


Documentation
-------------

The `typed` library currently supports the following types: `any`, `int`, `float`, `none`, `str`, `unicode`, `string`, `bool`, `date`, `datetime`, `list`, `dict` and `tuple`, as well as type unions and finite sets of values.

All types support the method `t.test(obj)`, which returns `True` if the value conforms to the type, and `False` otherwise.

All types also support methods `t.load(stored_obj)` and `t.save(obj)`, which are used for deserialization and serialization, respectively. The method `obj = t.load(stored_obj)` transforms the value from the specified format and adds all the necessary fields with default values, returning an object for which `t.test(obj)` return True. For any object that `t.test(obj)` return True, the method `t.save(obj)` will return an object appropriate for serialization in the format specified. If inappropriate object types are passed to methods `load` or `save`, a `ValueError` exception will be raised. Note that `load` and `save` might modify mutable objects, specifically `list` and `dict` objects, so that the statement `d = t.save(d)` is equivalent to `t.save(d)`.


### Formatting

All types also support the `t.format(fmt)` method, which specifies the format you want to save the type in. All types support custom encoding of specific values, specified by passing a `dict` with objects as keys and encodings as values.

```python
t = typed.int.format({1: 'one', 2: 'two'})

assert all([
		t.load('one') == 1, t.save(1) == 'one',
		t.load('two') == 2, t.save(2) == 'two',
		t.load(2) == 2, t.save(3) == 3,
	])
```

All types also support the `json` format.

```python
t1 = typed.json(typed.list(typed.int))
t2 = typed.dict({'a': typed.int}).format(typed.json)

assert all([
		t1.load('[1, 2, 3]') == [1, 2, 3], t1.save([1, 2, 3]) == '[1, 2, 3]',
		t2.load('{"a": 1}') == {'a': 1}, t2.save({'a': 2}) == '{"a": 2}',
	])
```

If available, the `typed.json` formatter uses the `ujson` library, otherwise it uses Python's own (slower) `json` serializer. If `ujson` serializer is used, `typed.json` supports an additional parameter `double_precision` that controls the number of float digits used when serializing floats.

```python
t1 = typed.json(typed.list(typed.float))
t2 = typed.json(typed.list(typed.float), double_precision=3)

assert all([
		t1.save([0.0001, 0.0011, 0.0056, 12345.6789]) == '[0.0001,0.0011,0.0056,12345.6789]',
		t2.save([0.0001, 0.0011, 0.0056, 12345.6789]) == '[0.0,0.001,0.006,12345.679]',
	])
```

Be careful when chaining formats:

```python
typed.date.format({datetime.date(2000, 1, 1): 'millennium'})
typed.date.format('%Y-%m-%d').format({'2000-01-01': 'millennium'})

typed.dict({'a': typed.int.default(0)}).format(typed.json).format({'{}': ''})
```

Specific types might support other formats as well.


### Type unions

The `typed` library supports arbitrary type unions, formed using the `|` operator. A union of types `t1`, `t1`, ..., <code>t<i>n</i></code> is a type which includes all values belonging to any of the types `t1`, `t2`, ..., <code>t<i>n</i></code>.

```python
t = typed.int | typed.string | typed.float

assert all([
		t.test(0),
		t.test('a'),
		t.test(0.1),
	])
```

The methods `load` and `save` of a type union will try loading or saving the object using all types in the union in the specified order.

```python
t = typed.date.format('%Y-%m-%d') | typed.date.format('%d/%m/%Y')

assert all([
		t.load('2013-05-07') == t.load('07/05/2013'),
		t.save(t.load('07/05/2013')) == '2013-05-07',
	])
```


#### `typed.int` type

The `typed.int` is the type of all integer values. In Python 2.x, it is a union of `int` and `long` types. In contrast to Python, `typed.bool` is not a subtype of `typed.int` and `typed.int.test(True)` will return `False`.

#### `typed.none` type

The `typed.none` type has a JSON-inspired alias `typed.null == typed.none`.

#### `typed.str` type

This is the `str` type of Python 2.x, and has an alias `typed.ascii == typed.str`.

#### `typed.string` type

This is the `basestring` type of Python 2.x, and is equivalent to `typed.string = typed.ascii | typed.unicode`.

#### `typed.date` type

This is the proper `date` type, which doesn't test `True` for instances of `datetime`. Its `format` method accepts standard Python date formatting strings.

#### `typed.datetime` type

Its `format` method accepts standard Python datetime formatting strings.

####	`typed.set(values...)` type

This type constructor accepts any number of values and produces a type which tests `True` for any of these values. For example, the `bool` type could be impleneted as `bool = typed.set(True, False)`.

#### `typed.list(type)` type

The type constructor `typed.list(t)` produces a type of arbitrary length lists, whose elements are all of type `t`. The `load` and `save` methods of this type modify the argument, which might produce unexpeced results in case of failure. This is also the reason you should take care when using `typed.list` in type unions.

#### `typed.dict({'field': type, ...})` type

This type constructor produces a type of dictionaries that have specified fields with values of specified types. Fields might be designated `optional` or have `defaul` values (all fields with `default` values are also `optional`). If `typed.dict` type is `trimmed`, it will accept dictionaries with additional fields, while `load` and `save` methods will remove these fields. The `load` and `save` methods of this type modify the argument, which might produce unexpeced results in case of failure. This is also the reason you should take care when using `typed.dict` in type unions.

```python
t1 = typed.dict({
		'a': typed.int,
		'b': typed.string.optional,
		'c': (typed.string | typed.none).default(None),
		'd': typed.optional,
	})
t2 = t1.trimmed

assert all([
		not t1.test({}), t1.test({'a': 1}), not t1.test({'a': 2, 'e': None}),
		t1.load({'a': 3}) == {'a': 3, 'c': None},
		t1.save({'a': 4, 'b': 'foo', 'c': None, 'd': [1, 2, 3]}) == {'a': 4, 'b': 'foo', 'd': [1, 2, 3]},
		t2.test({'a': 5, 'e': None}),
		t2.load({'a': 6, 'e': 'something'}) == {'a': 6, 'c': None},
	])
```

You can use aliases `typed.optional == typed.any.optional` and `typed.default(x) == typed.any.default(x)`.

#### `typed.tuple(types...)` type

This type constructor produces the type of tuples that have elements of the specified types. Its `format` method accepts `typed.list` as an argument, in which case the tuple is encoded as a `list` (useful when loading/saving JSON).

```python
t = typed.tuple(typed.string, typed.int, typed.float).format(typed.list).format(typed.json)

assert t.load('["1", 2, 3.0]') == ('1', 2, 3.0)
```
