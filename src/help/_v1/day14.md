## Functions are values too

In Python, a function is a value just like a number or a list. You can store it in a variable, pass it into another function, or return it from one:

```python
def shout(text):
    return text.upper() + "!"

yell = shout             # no brackets: the function itself, not a call
print(yell("ssd ready"))

def apply_twice(func, value):
    return func(func(value))

print(apply_twice(lambda n: n * 10, 3))   # 300
```

A function that takes or returns another function is called a **higher-order function**.

## `map`: do something to every item

```python
sizes = [256, 512, 1000]
in_tb = map(lambda gb: gb / 1000, sizes)
print(list(in_tb))       # wrap in list() to see the results
```

## `filter`: keep items that pass a test

```python
healths = [95, 12, 60, 3]
good = filter(lambda h: h >= 20, healths)
print(list(good))
```

## `reduce`: squash a list into one value

`reduce` lives in the `functools` module. It combines items two at a time:

```python
from functools import reduce
total = reduce(lambda a, b: a + b, [1, 2, 3, 4])   # ((1+2)+3)+4
print(total)
```

## `sorted` with a `key`

Pass a function as `key` to choose **what** to sort by:

```python
drives = [{"id": "A", "health": 40}, {"id": "B", "health": 99}]
best_first = sorted(drives, key=lambda d: d["health"], reverse=True)
print(best_first)
```

`min()` and `max()` accept `key=` too!

## Closures: functions that remember

```python
def make_multiplier(n):
    return lambda x: x * n       # remembers n

triple = make_multiplier(3)
print(triple(10))
```

## Decorators: wrap a function with extra behaviour

A **decorator** takes a function and returns a new function that does something extra, then calls the original. The `@` symbol applies it:

```python
def loud(func):
    def wrapper(*args):
        print(">>> calling", func.__name__)
        return func(*args)
    return wrapper

@loud
def add(a, b):
    return a + b

print(add(2, 3))
```

`@loud` above `def add` is the same as writing `add = loud(add)` afterwards. `func.__name__` is the function's name as a string.

## Your task

You're given `ssds`, a list of drive dicts.

1. `gbs`: every drive's `gb`, using **`map`**
2. `healthy`: drives with `health` of 20 or more, using **`filter`**
3. `total_gb`: the sum of `gbs`, using **`reduce`**
4. `ranked`: the drives sorted by `health`, **highest first**
5. A decorator `logged` that prints `Running <function name>` before calling the function
6. Put `@logged` on the `make_label` function that's already written for you
