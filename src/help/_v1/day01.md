## What is Python?

Python is a **programming language**: a way to write instructions a computer can follow. A list of instructions is called a **program** (or **code**). Python reads your code **from top to bottom, one line at a time**.

## Your first instruction: `print()`

`print()` tells Python to show something on the screen. Anything written **between quotes** is called a **string** (a piece of text):

```python
print("Hello, factory!")
print("I am learning Python")
```

Press **▶ Run** on the box above to try it. You can edit any example box too!

## Python as a calculator

Numbers don't need quotes. Python can do maths with them:

| Symbol | Meaning | Example | Result |
|---|---|---|---|
| `+` | add | `3 + 2` | `5` |
| `-` | subtract | `3 - 2` | `1` |
| `*` | multiply | `3 * 2` | `6` |
| `/` | divide | `3 / 2` | `1.5` |
| `**` | power | `3 ** 2` | `9` |
| `%` | remainder | `3 % 2` | `1` |
| `//` | whole-number divide | `3 // 2` | `1` |

```python
print(3 + 2)
print(10 / 4)
print(2 ** 10)
```

⚠️ `print("3 + 2")` shows the text `3 + 2`, but `print(3 + 2)` shows `5`. The quotes make it text!

## Comments

A line starting with `#` is a **comment**. Python ignores it. Comments are notes for humans:

```python
# This line is ignored by Python
print("This line runs")  # a comment can go at the end of a line too
```

## Data types (a sneak peek)

Every value in Python has a **type**. You'll meet them all properly over the next few days:

- `int`: whole numbers like `7` or `-3`
- `float`: decimal numbers like `3.14`
- `str`: text (strings) like `"hello"`
- `bool`: `True` or `False`
- `list`, `tuple`, `set`, `dict`: collections of values (Days 5–8)

`type()` tells you a value's type:

```python
print(type(7))
print(type(3.14))
print(type("hello"))
```

## Your task

1. Print the message `Factory online`
2. Print how many **hours** the factory runs in a week. It runs 24 hours a day, 7 days a week. Let Python do the multiplying: don't type the answer yourself!
