## When things go wrong on purpose

Yesterday's errors were **bugs**: mistakes in the code. But some errors are **expected**. A file might be missing, a user might type "abc" when asked for a number, or a motherboard might be faulty. Your program shouldn't crash just because one board out of a thousand is broken!

**Exception handling** lets you catch errors and decide what to do.

## `try` and `except`

```python
try:
    number = int("abc")
    print("This line never runs")
except ValueError:
    print("That wasn't a number, but we kept going!")
print("Program continues")
```

Python **tries** the indented block. If an error happens, it jumps straight to the matching `except`, and the program carries on.

## Catching different errors differently

```python
stock = {"DDR5": 10}
for key in ["DDR5", "DDR9"]:
    try:
        print(key, "→", 100 // stock[key])
    except KeyError:
        print(key, "isn't stocked")
    except ZeroDivisionError:
        print("Out of stock!")
```

## Getting the error message with `as`

```python
try:
    int("12GB")
except ValueError as err:
    print("Problem:", err)
```

## `else` and `finally`

```python
for text in ["42", "oops"]:
    try:
        n = int(text)
    except ValueError:
        print(text, "→ failed")
    else:
        print(text, "→ worked:", n)       # only if NO error
    finally:
        print("   checked", text)          # ALWAYS runs
```

## Raising your own errors

Use `raise` when **your** code spots a problem:

```python
def check_temp(temp):
    if temp > 100:
        raise ValueError(f"{temp}°C is too hot!")
    return True

try:
    check_temp(130)
except ValueError as err:
    print("Caught:", err)
```

⚠️ Only catch the errors you **expect**. A bare `except:` hides real bugs, so name the error type.

## Your task

You're given `boards` (a list of motherboard dicts) and `tester`. Calling `tester.install(board)` either works, or raises:
- `ValueError` if the board has blown a capacitor
- `KeyError` if the board is missing its BIOS chip

For **every** board:
1. **Try** to install it
2. On a `ValueError`: print a message including the error, and add its serial to `blown`
3. On a `KeyError`: add its serial to `no_bios`
4. If there was **no** error (`else`): add its serial to `installed`
5. **Always** (`finally`): add 1 to `checked`

Then write `check_volts(volts)`, which **raises** a `ValueError` if `volts` is over `1.5` and otherwise returns `True`.
