# Functions

A **function** is a named block of code you can run whenever you like. You've been *using* functions since your first line (`harvest()`, `print()`). Now you can make your own with `def`.

## Defining and calling

```python
def greet():
    print("Welcome to ByteWorks!")

greet()
greet()
```

The indented body only runs when you **call** the function.

## Parameters and `return`

```python
def square(n):
    return n * n

print(square(7) + 1)
```

- **Parameters** are inputs: `def add(a, b):`
- `return` hands a result back to whoever called the function (and stops the function)
- A function without `return` gives back `None`

## Defaults and keyword arguments

```python
def make_chip(cores, clock=3.0):
    return f"{cores} cores @ {clock} GHz"

print(make_chip(8))
print(make_chip(clock=5.0, cores=16))
```

## Any number of arguments: `*args`

```python
def total(*numbers):
    result = 0
    for n in numbers:
        result += n
    return result

print(total(1, 2, 3))
```

## Functions for the drone

A function that sweeps one floor can be reused for every floor:

```py
def tend(part):
    for col in range(3):
        for row in range(3):
            if can_harvest():
                harvest()
            if get_part() == None:
                place(part)
            move(North)
        move(East)

while True:
    goto_floor(Floor.RAM)
    tend(Part.RAM)
    goto_floor(Floor.CPU)
    tend(Part.CPU)
```

(On the RAM floor every tile already has RAM, so `place` never runs there.)

## `global`

A function can't change a variable outside itself unless you say `global name` inside it. Returning a value is usually neater.

## Try this

Write `sweep()` and `lap_count()` functions, and use them to print how many laps your drone has done.
