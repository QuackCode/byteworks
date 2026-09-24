# Higher-order Functions

In Python, a function is a value like any other. You can store it, pass it into another function, or return it:

```python
def shout(text):
    return text.upper() + "!"

yell = shout                 # no brackets: the function itself
print(yell("ssd ready"))

def apply_twice(func, value):
    return func(func(value))

print(apply_twice(lambda n: n * 10, 3))
```

## `map`, `filter` and `sorted`

```python
sizes = [256, 512, 1000]
print(list(map(lambda gb: gb / 1000, sizes)))        # do something to every item
print(list(filter(lambda h: h >= 20, [95, 12, 60])))  # keep items that pass a test
drives = [{"id": "A", "health": 40}, {"id": "B", "health": 99}]
print(sorted(drives, key=lambda d: d["health"], reverse=True))
print(max(drives, key=lambda d: d["health"]))
```

`reduce` (from `functools`) combines items two at a time, but a plain `sum()` or loop is usually clearer.

## Closures: functions that remember

```python
def make_multiplier(n):
    return lambda x: x * n

triple = make_multiplier(3)
print(triple(10))
```

## Decorators

A **decorator** wraps a function with extra behaviour. `@loud` above a `def` is the same as `add = loud(add)`:

```python
def loud(func):
    def wrapper(*args):
        print("calling", func.__name__)
        return func(*args)
    return wrapper

@loud
def add(a, b):
    return a + b

print(add(2, 3))
```

## Visit the scarcest part first

```py
def tend(part):
    for col in range(3):
        for row in range(3):
            if can_harvest():
                harvest()
            if get_part() == None:
                place(part)
            if row < 2:
                if col % 2 == 0:
                    move(North)
                else:
                    move(South)
        if col < 2:
            move(East)
    move(West)
    move(West)
    move(South)
    move(South)

floors = [Floor.RAM, Floor.CPU, Floor.SSD]
while True:
    for f in sorted(floors, key=lambda f: num_items(f)):
        goto_floor(f)
        tend(f)
```

## Try this

Write a function `best_floor()` that uses `min(..., key=...)` to pick the floor you have the fewest parts from.
