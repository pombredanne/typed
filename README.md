Typed - a Python data validation library
========================================

This library allows type tests and transformation and can be used for data loading, storing and validation.


Usage
-----

Simple type-checking:

```python
import typed

t1 = typed.int | typed.string

assert t1.test('abc')
assert t1.test(u'xyz')
assert t1.test(30)
assert not t1.test(1.2)
assert not t1.test(True)
assert not t1.test(None)

t2 = typed.list(typed.int)

assert t2.test([1, 2, 3])
assert t2.test([])
assert not t2.test(['a', 'b', 'c'])

t3 = typed.list(typed.int | typed.string)

assert t3.test([1, 'a', 2, 'b'])

t4 = typed.list(typed.int) | typed.list(typed.string)

assert t4.test([1, 2, 3])
assert t4.test(['a', 'b', 'c'])
assert not t4.test([1, 'a', 2, 'b'])

t5 = typed.set(1, 2, 3)

assert t5.test(2)
assert not t5.test(4)

t6 = typed.dict({
		'a': typed.int,
		'b': typed.bool.optional,
		'c': (typed.int | typed.none).optional,
	})
```
