# Variables & Operators

## Variables: labelled boxes

A **variable** stores a value under a name so you can use it later. You make one with `=`:

```python
machines = 3
factory_name = "ByteWorks"
print(factory_name, machines)
```

`=` means **"store this value in this box"**. It isn't the maths *equals*! You can change a variable later, and the new value replaces the old one.

### Naming rules
- Use letters, numbers and underscores: `ram_count`, `lap2`
- A name can't **start** with a number, or contain spaces
- Names are case-sensitive: `Laps` and `laps` are different boxes
- Python style is **snake_case**: lowercase words joined by `_`

## The four basic types

```python
laps = 3              # int   (whole number)
speed = 1.5           # float (decimal number)
name = "Drone"        # str   (text, always in quotes)
running = True        # bool  (True or False, capital letter!)
print(type(laps), type(speed), type(name), type(running))
```

## Operators

| Kind | Operators |
|---|---|
| Maths | `+ - * /`, `//` (whole divide), `%` (remainder), `**` (power) |
| Update | `+=`, `-=`, `*=` (`x += 1` means `x = x + 1`) |
| Compare (gives True/False) | `==`, `!=`, `>`, `<`, `>=`, `<=` |
| Logic | `and`, `or`, `not` |

```python
parts = 17
print(parts // 4, parts % 4)    # 4 boxes of 4, 1 left over
print(parts > 10 and parts < 20)
parts += 3
print(parts)
```

⚠️ `=` **stores** a value and `==` **compares** two values. Mixing them up is the #1 beginner mistake!

## Handy built-in functions

`int("42")`, `float("2.5")`, `abs(-5)`, `min(3, 9)`, `max(3, 9)`, `round(3.7)`, `type(x)`

## `num_items()`: how many parts you have

```py
while num_items(Part.RAM) < 50:
    harvest()
    move(North)
print("50 RAM!")
```

## Counting with a variable

```py
laps = 0
while True:
    harvest()
    move(North)
    laps = laps + 1
    print(laps)
```

## Try this

Make the drone stop by itself when you have 100 RAM, and print how many moves it took.
