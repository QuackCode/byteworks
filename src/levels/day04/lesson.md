## Strings in depth

A **string** is text in quotes. Single `'...'` or double `"..."` quotes both work. Triple quotes `"""..."""` let a string span several lines.

```python
part = "RAM stick"
print(part + " x2")       # join strings with +  (concatenation)
print(part * 3)           # repeat a string
print(len(part))          # 9 characters (spaces count!)
```

`"\n"` inside a string means *new line*, and `"\t"` means *tab*.

## Indexing: getting one character

Each character has a position called its **index**. Python counts from **0**!

```
 R   A   M   -   0   0   4   2
 0   1   2   3   4   5   6   7     (from the left)
-8  -7  -6  -5  -4  -3  -2  -1     (from the right)
```

```python
code = "RAM-0042"
print(code[0])    # R
print(code[-1])   # 2  (negative = count from the end)
```

## Slicing: getting a chunk

`text[start:end]` takes characters from `start` **up to but not including** `end`. Leave a side blank to go all the way to that end:

```python
code = "RAM-0042"
print(code[0:3])   # RAM
print(code[:3])    # RAM   (same thing)
print(code[4:])    # 0042
print(code[-4:])   # 0042  (last 4 characters)
print(code[::-1])  # 2400-MAR  (reversed!)
```

## String methods

A **method** is a function that belongs to a value, and you call it with a dot. Methods give back a **new** string and don't change the original (strings can't be changed: they're *immutable*).

| Method | Does | Example → result |
|---|---|---|
| `.upper()` / `.lower()` | change case | `"ram".upper()` → `"RAM"` |
| `.strip()` | remove spaces at both ends | `"  hi  ".strip()` → `"hi"` |
| `.replace(a, b)` | swap text | `"a-b".replace("-", "")` → `"ab"` |
| `.startswith(x)` / `.endswith(x)` | True/False check | `"RAM-1".startswith("RAM")` → `True` |
| `.find(x)` | position of x (or -1) | `"RAM-1".find("-")` → `3` |
| `.count(x)` | how many times x appears | `"0042".count("0")` → `2` |
| `.split(x)` | break into a list | `"a,b".split(",")` → `["a", "b"]` |
| `.isdigit()` | is it all numbers? | `"0042".isdigit()` → `True` |
| `.title()` / `.capitalize()` | tidy capitals | `"byte works".title()` → `"Byte Works"` |

```python
raw = "  gpu-0107  "
clean = raw.strip().upper()     # you can chain methods!
print(clean)
print(clean.replace("-", " / "))
```

## f-strings: the best way to build text

Put `f` before the quotes, then drop variables straight in with `{}`:

```python
kind = "CPU"
speed = 4.2
print(f"This {kind} runs at {speed} GHz")
print(f"Double speed: {speed * 2} GHz")   # you can even do maths inside {}
```

(Older ways you'll see online: `"%s runs" % kind` and `"{} runs".format(kind)`. f-strings are cleaner.)

## Your task

You're given `raw_code`, a messy code like `"  ram-0042  "`.

1. `clean`: remove the spaces and make it UPPERCASE → `"RAM-0042"`
2. `part_type`: the first 3 characters → `"RAM"`
3. `number`: the last 4 characters → `"0042"`
4. `label`: an f-string like `"RAM #0042"`, then **print** it
5. `sku`: `clean` with the dash removed → `"RAM0042"`
6. `is_ram`: `True` if `clean` starts with `"RAM"`
