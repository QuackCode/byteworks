## Making decisions with `if`

So far your code has run every line, top to bottom. **Conditionals** let your code choose what to do:

```python
temp = 95
if temp > 90:
    print("Too hot! Rejecting chip.")
print("Next chip please")
```

The rules:
- `if` is followed by a **condition** (anything that's `True` or `False`) and a **colon** `:`
- The lines that belong to the `if` are **indented** (4 spaces). They only run when the condition is `True`
- When the indentation stops, the `if` block is over

## `else`: otherwise

```python
temp = 70
if temp > 90:
    print("Reject")
else:
    print("Keep")
```

## `elif`: more than two choices

`elif` means "else, if…". Python checks each condition **from top to bottom** and runs **only the first** one that's `True`:

```python
clock = 3.2
if clock >= 4.0:
    kind = "fast"
elif clock >= 2.5:
    kind = "medium"
else:
    kind = "slow"
print(kind)     # medium
```

🧠 **Order matters!** If you check `clock >= 2.5` first, a 4.4 GHz chip would be called "medium", because that condition is already True and Python stops looking.

## Combining conditions

Use `and`, `or` and `not` from Day 3:

```python
clock, temp = 4.4, 55
if clock >= 4.0 and temp < 60:
    print("Premium chip! ⭐")
if temp < 0 or temp > 120:
    print("Sensor broken")
```

## Nested conditions

You can put an `if` inside another `if` (indent twice). Often `and` is neater, though:

```python
powered, temp = True, 95
if powered:
    if temp > 90:
        print("Powered but overheating")
```

## One-line conditional

`value = A if condition else B`:

```python
temp = 50
status = "hot" if temp > 90 else "ok"
print(status)
```

## Your task

You're given `cpu`, a dictionary like `{"serial": "CPU-1201", "clock_ghz": 4.4, "temp_c": 55}`. Set `grade`:

| Rule (check in this order!) | grade |
|---|---|
| `temp_c` is **over** 90 (overheated: faulty) | `"REJECT"` |
| `clock_ghz` is **at least** 4.0 | `"GAMING"` |
| `clock_ghz` is **at least** 2.5 | `"OFFICE"` |
| anything else (too slow) | `"REJECT"` |

Then set `premium` to `True` only if the grade is `"GAMING"` **and** `temp_c` is under 60. Your code will be tested on lots of different chips!
