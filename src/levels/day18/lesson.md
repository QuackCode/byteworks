## Regular expressions: patterns for text

A **regular expression** (regex) is a tiny language for describing **patterns** in text: "a capital letter, then 4 digits", "anything that looks like an email", and so on. Python's `re` module uses them.

```python
import re
print(re.findall(r"\d+", "Order 42 needs 7 boards and 128 chips"))
```

The `r"..."` is a **raw string**: it stops Python treating `\` specially. Always use it for patterns.

## The building blocks

| Pattern | Matches |
|---|---|
| `abc` | exactly the text abc |
| `\d` | any digit 0–9 |
| `\w` | a letter, digit or `_` |
| `\s` | whitespace (space, tab, newline) |
| `.` | any character |
| `[A-Z]` | one capital letter |
| `[aeiou]` | one of these letters |
| `^` | the **start** of the text |
| `$` | the **end** of the text |

## Repeating things

| Pattern | Means |
|---|---|
| `x*` | 0 or more x |
| `x+` | 1 or more x |
| `x?` | 0 or 1 x (optional) |
| `x{4}` | exactly 4 x |
| `x{2,5}` | 2 to 5 x |

```python
import re
print(re.findall(r"[A-Z]{3}-\d+", "Parts: RAM-12, cpu-4, GPU-7788"))
```

## The main functions

```python
import re
text = "MB-2041-AX shipped"
print(re.match(r"MB", text))        # matches at the START? gives a match object or None
print(re.search(r"\d{4}", text))    # found ANYWHERE?
print(re.findall(r"\d", text))      # list of every match
print(re.sub(r"\d", "#", text))     # replace every match
print(re.split(r"-", "MB-2041-AX")) # split on a pattern
```

A match object counts as `True` in an `if`, and `None` counts as `False`:

```python
import re
for code in ["MB-2041-AX", "MB-20X1-AX"]:
    if re.match(r"MB-\d{4}", code):
        print(code, "looks real")
    else:
        print(code, "is FAKE")
```

## Anchors matter! ⚓

`re.match(r"MB-\d{4}-[A-Z]{2}", "MB-2041-AXZ")` **matches**, because it only checks that the start fits. Add `^` and `$` to demand the **whole** text fits:

```python
import re
pattern = r"^MB-\d{4}-[A-Z]{2}$"
print(bool(re.match(pattern, "MB-2041-AX")))    # True
print(bool(re.match(pattern, "MB-2041-AXZ")))   # False
```

## Your task

You're given `scans` (a list of serial strings), `memo` (some text) and `phone` (a phone number string).

1. `pattern`: a regex for a **genuine** serial: `MB-`, 4 digits, `-`, 2 capital letters, and **nothing else**
2. `genuine`: the scans that match (in order)
3. `counterfeit`: the scans that don't
4. `batch_numbers`: every 4-digit number in `memo`, using `re.findall`
5. `redacted`: `phone` with every digit replaced by `#`, using `re.sub`
