# Strings & f-strings

A **string** is text in quotes. Single `'...'` or double `"..."` quotes both work.

```python
part = "RAM stick"
print(part + " x2")       # joining (concatenation)
print(part * 2)           # repeating
print(len(part))          # spaces count!
```

## Indexing and slicing

```python
code = "RAM-0042"
print(code[0], code[-1])   # first and last character
print(code[:3])            # RAM
print(code[-4:])           # 0042
print(code[::-1])          # reversed
```

## String methods

Methods give back a **new** string. Strings can never be changed.

| Method | Example → result |
|---|---|
| `.upper()` / `.lower()` | `"ram".upper()` → `"RAM"` |
| `.strip()` | `"  hi  ".strip()` → `"hi"` |
| `.replace(a, b)` | `"a-b".replace("-", "")` → `"ab"` |
| `.startswith(x)` / `.endswith(x)` | `"RAM-1".startswith("RAM")` → `True` |
| `.split(x)` | `"a,b".split(",")` → `["a", "b"]` |
| `.find(x)` / `.count(x)` | position / how many |
| `.isdigit()` | `"42".isdigit()` → `True` |

```python
raw = "  gpu-0107  "
print(raw.strip().upper().split("-"))
```

## f-strings: the best way to build text

Put `f` before the quotes and drop values in with `{}`:

```python
speed = 4.2
print(f"This chip runs at {speed} GHz, {speed * 2} when boosted")
```

## A status report

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

laps = 0
while True:
    tend(Part.RAM)
    laps += 1
    print(f"Lap {laps}: RAM {num_items(Part.RAM)}")
```

## 🎯 Quest

**print() an f-string that shows how much RAM you have.** Doing it lets you buy **Comprehensions & lambda** (you'll still need its parts).

An f-string drops values straight into text, like `print(f"RAM: {num_items(Part.RAM)}")`.
