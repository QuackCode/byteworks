## Variables: labelled boxes

A **variable** stores a value under a name so you can use it later. You make one with `=`:

```python
machines = 3
factory_name = "ByteWorks"
print(factory_name)
print(machines)
```

`=` means **"store this value in this box"**. It's not the maths *equals*! You can change a variable later, and the new value replaces the old one.

### Naming rules
- Use letters, numbers and underscores: `power_kw`, `machine2`
- A name can't **start** with a number (`2machine` ❌) or contain spaces (`power kw` ❌)
- Names are case-sensitive: `Machines` and `machines` are different boxes
- Python style is **snake_case**: lowercase words joined by `_`

## The four basic types

```python
machines = 3          # int   (whole number)
power_kw = 12.5       # float (decimal number)
factory_name = "BW"   # str   (text: always in quotes)
is_open = True        # bool  (True or False: capital letter!)
print(type(machines), type(power_kw), type(factory_name), type(is_open))
```

You can make several variables on one line too: `a, b = 1, 2`

## Built-in functions

Python comes with ready-made tools called **built-in functions**. You've already met `print()` and `type()`. Some more:

| Function | What it does | Example |
|---|---|---|
| `len()` | length (how many characters/items) | `len("hello")` → `5` |
| `int()` | convert to a whole number | `int("42")` → `42` |
| `float()` | convert to a decimal | `float("2.5")` → `2.5` |
| `str()` | convert to text | `str(42)` → `"42"` |
| `round()` | round a number | `round(3.7)` → `4` |
| `abs()` | distance from zero | `abs(-5)` → `5` |
| `min()` / `max()` | smallest / biggest | `max(3, 9, 4)` → `9` |
| `input()` | ask the user to type something | `input("Name? ")` |

```python
word = "motherboard"
print(len(word))
print(max(12, 99, 45))
print(int("7") + 3)
```

## Asking questions with `input()`

`input()` shows a question and **gives back** whatever the user types, **always as a string**. Save it in a variable:

```python
operator = input("What is your name? ")
print("Welcome,", operator)
```

(In ByteWorks, a pretend operator does the typing for you.)

`print()` can show several things at once: separate them with commas and it puts a space between each one.

## Your task

Set up the control panel:
1. `factory_name` = the text `ByteWorks`
2. `machines` = the whole number `3`
3. `power_kw` = the decimal `12.5`
4. `is_open` = `True`
5. `name_length` = the length of `factory_name` (use `len()`, don't count by hand!)
6. Ask the operator their name with `input()`, store it in `operator`, then print `Welcome, <their name>`
