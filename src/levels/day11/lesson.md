## Functions: build a machine once, use it forever

A **function** is a named, reusable block of code. You've been *using* functions since Day 1 (`print`, `len`, `input`). Now you'll **make** your own with `def`:

```python
def greet():
    print("Welcome to the CPU floor!")

greet()    # "call" the function to run it
greet()
```

The indented block only runs when you **call** the function by writing its name with brackets.

## Parameters: giving a function inputs

```python
def greet(name):
    print("Welcome,", name)

greet("Ada")
greet("Linus")
```

`name` is a **parameter**, a variable that gets its value when the function is called. You can have several: `def add(a, b):`.

## `return`: giving back a result

`print` shows a value on screen, but `return` **hands it back** to whoever called the function, so they can store it or use it:

```python
def square(n):
    return n * n

result = square(7)
print(result + 1)     # 50
```

⚠️ A function without `return` gives back `None`. Once `return` runs, the function stops immediately.

## Default values

A parameter can have a default, used when nothing is passed in:

```python
def make_chip(cores, clock_ghz=3.0):
    return f"{cores} cores @ {clock_ghz} GHz"

print(make_chip(8))              # uses the default 3.0
print(make_chip(8, 4.5))
print(make_chip(clock_ghz=5.0, cores=16))   # keyword arguments: any order!
```

## Any number of arguments: `*args`

A `*` before a parameter collects **all** the extra arguments into a tuple:

```python
def total(*numbers):
    result = 0
    for n in numbers:
        result += n
    return result

print(total(1, 2, 3))
print(total(10, 20))
```

(`**kwargs` does the same for keyword arguments, collecting them into a dict.)

## Functions can call functions

```python
def is_hot(temp):
    return temp > 90

def status(temp):
    return "HOT" if is_hot(temp) else "OK"

print(status(95))
```

## Your task

1. `build_cpu(cores, clock_ghz=3.0)`: **return** a dict `{"cores": ..., "clock_ghz": ..., "score": cores × clock_ghz}`
2. `is_faulty(cpu)`: **return** `True` if the chip's `clock_ghz` is `0` **or** its `temp_c` is over `100`, otherwise `False`
3. `total_cores(*cpus)`: **return** the total number of cores across any number of CPU dicts

The checker will call your functions with lots of different values.
