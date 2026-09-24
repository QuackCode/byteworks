## Tuples: lists that can't change

A **tuple** is like a list, but once it's made it can **never be changed**. It's *immutable*, just like a string. Tuples use round brackets `()`:

```python
spec = (32, 5600)          # 32 GB, 5600 MHz
print(spec)
print(spec[0])             # 32  (indexing works like lists)
print(len(spec))           # 2
print(type(spec))
```

A tuple with only one item needs a trailing comma: `(5,)`. Without it, `(5)` is just the number 5!

## Why use a tuple?

Use a tuple for values that **belong together and shouldn't change**: coordinates `(x, y)`, a date `(2026, 9, 24)`, or a part's spec. If someone tries to change it, Python stops them:

```python
spec = (32, 5600)
spec[0] = 31     # 💥 TypeError: tuples can't be changed
```

## Unpacking

You can pull a tuple's values into separate variables in one line:

```python
spec = (32, 5600)
capacity, speed = spec
print(capacity, "GB at", speed, "MHz")
```

## What you *can* do with tuples

```python
specs = ((32, 5600), (16, 4800), (32, 5600))
print(specs.count((32, 5600)))   # 2: how many match
print(specs.index((16, 4800)))   # 1: position of the first match
print((16, 4800) in specs)       # True
both = (1, 2) + (3,)             # joining makes a NEW tuple
print(both)
```

Convert between them: `list(my_tuple)` makes a list you can edit, and `tuple(my_list)` makes it a tuple again.

## Your task

You're given `specs`, a list of `(capacity, speed)` tuples from today's batch.

1. `STANDARD`: the tuple `(32, 5600)`. (A name in CAPITALS means "this is a constant: don't change it".)
2. Unpack `STANDARD` into `capacity` and `speed`
3. `matching`: how many specs in the batch equal `STANDARD`
4. `first_match`: the position of the first matching spec
5. `fast_spec`: a **new** tuple with the same capacity but speed `6400`
