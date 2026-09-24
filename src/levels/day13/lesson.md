## List comprehensions: loops in one line

You've built lists like this many times:

```python
numbers = [1, 2, 3, 4, 5]
doubled = []
for n in numbers:
    doubled.append(n * 2)
print(doubled)
```

A **list comprehension** does the same thing in one line:

```python
numbers = [1, 2, 3, 4, 5]
doubled = [n * 2 for n in numbers]
print(doubled)
```

Read it as: **"`n * 2`, for each `n` in `numbers`"**.

## Adding a filter with `if`

```python
numbers = [1, 2, 3, 4, 5, 6]
evens = [n for n in numbers if n % 2 == 0]
print(evens)
big_doubled = [n * 2 for n in numbers if n > 3]
print(big_doubled)
```

The pattern is `[what_to_keep  for item in collection  if condition]`.

## Works on anything you can loop over

```python
print([letter.upper() for letter in "ssd"])
print([i for i in range(10) if i % 3 == 0])
```

## Flattening a list of lists

Two `for`s, in the same order you'd write nested loops:

```python
shelves = [["A1", "A2"], ["B1", "B2", "B3"]]
slots = [slot for row in shelves for slot in row]
print(slots)
```

## Dictionary comprehensions

Same idea with `{key: value ...}`:

```python
drives = [("SSD-01", 512), ("SSD-02", 1000)]
sizes = {serial: gb for serial, gb in drives}
print(sizes)
squares = {n: n * n for n in range(1, 5)}
print(squares)
```

## Lambda: tiny one-line functions

A **lambda** is a small, nameless function written in one line: `lambda inputs: result`

```python
double = lambda x: x * 2
print(double(21))
add = lambda a, b: a + b
print(add(3, 4))
```

It's the same as `def double(x): return x * 2`. Lambdas are handy for short jobs, especially tomorrow when you pass functions into other functions.

## Your task

You're given `ssds` (a list of dicts like `{"serial": "SSD-0301", "gb": 1000, "health": 87}`) and `shelves` (a list of lists of slot names). A drive is **dead** if its `health` is below 20. Use comprehensions only, with **no `.append()`**!

1. `working`: only the drives with `health` of 20 or more
2. `serials`: the serial of every **working** drive
3. `to_tb`: a **lambda** that turns GB into TB (divide by 1000)
4. `sizes_tb`: each working drive's size in TB, using `to_tb`
5. `capacity`: a **dict** mapping each working drive's serial → its `gb`
6. `all_slots`: every slot from `shelves` in one flat list
