# Exceptions

## Reading errors

When Python can't carry on, it stops with an **error** (an *exception*). The message tells you:

1. **Which line** the problem is on
2. **What type** of error it is
3. **What went wrong**

The error types you'll meet most:

| Error | Usually means |
|---|---|
| `SyntaxError` | a missing bracket, quote or colon |
| `IndentationError` | wrong spacing at the start of a line |
| `NameError` | a typo, or using a name before creating it |
| `TypeError` | mixing types, like `"Count: " + 5` |
| `ValueError` | right type, bad value, like `int("abc")` |
| `IndexError` | a list position that doesn't exist |
| `KeyError` | a dictionary key that doesn't exist |
| `ZeroDivisionError` | dividing by zero |
| `FaultyBoardError` | you harvested a faulty motherboard |

**How to debug:** run it, find the line, read the type and message, fix that one thing, run again. Adding `print()` to see what's in your variables is one of the best tricks there is.

## Catching errors with `try` / `except`

```python
try:
    number = int("abc")
except ValueError:
    print("That wasn't a number, but we kept going!")
print("Program continues")
```

If the `try` block raises an error, Python jumps to the matching `except` instead of stopping.

## Several errors, `as`, `else`, `finally`

```python
for text in ["42", "oops"]:
    try:
        n = int(text)
    except ValueError as err:
        print("Problem:", err)
    else:
        print("Worked:", n)          # only if there was no error
    finally:
        print("Checked", text)       # always runs
```

## Raising your own

```python
def check_temp(temp):
    if temp > 100:
        raise ValueError(f"{temp} is too hot!")
    return True

try:
    check_temp(130)
except ValueError as err:
    print("Caught:", err)
```

## Faulty boards, the easy way

```py
goto_floor(Floor.BOARD)
while True:
    try:
        if can_harvest():
            harvest()
    except FaultyBoardError:
        place(Part.BOARD)
    move(North)
```

⚠️ ByteWorks doesn't allow a bare `except:`. Always name the error you expect. A bare `except:` would also catch the **Stop** button!

## Try this

Rewrite your motherboard code using `try`/`except` instead of `is_faulty()`. Which version is easier to read?
