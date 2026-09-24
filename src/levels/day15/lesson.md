## Errors are your friends (really!)

When Python can't run your code, it stops and shows an **error**, often called an **exception**. The message tells you:

1. **Which line** the problem is on
2. **What type** of error it is
3. **A description** of what went wrong

Professional programmers see errors all day long. The skill isn't avoiding them, it's **reading them calmly**.

## The error types you'll meet most

### `SyntaxError`: Python can't even read it
```python
print("hello"
```
Missing brackets, quotes or colons. Python doesn't run *anything* until it's fixed.

### `NameError`: unknown name
```python
stock = 5
print(stok)
```
A typo, or using a variable before creating it.

### `TypeError`: wrong type for the job
```python
count = 5
print("Count: " + count)
```
You can't `+` a string and a number. Fix it with `str(count)` or an f-string.

### `IndexError`: position doesn't exist
```python
drives = ["A", "B", "C"]
print(drives[3])
```
3 items means positions 0, 1, 2. The last one is `drives[-1]` or `drives[len(drives) - 1]`.

### `KeyError`: key isn't in the dict
```python
ssd = {"serial": "SSD-01"}
print(ssd["Serial"])
```
Keys are **case-sensitive**!

### `ValueError`: right type, bad value
```python
print(int("2000GB"))
```
`int()` accepts a string, but only one that looks like a whole number.

### `AttributeError`: no such method
```python
drives = []
drives.push("A")
```
Lists use `.append()`. (`push` is from other languages.)

### Others
- `ZeroDivisionError`: dividing by 0
- `ModuleNotFoundError`: `import` of something that doesn't exist or isn't installed
- `IndentationError`: wrong spacing at the start of a line
- `FileNotFoundError`: opening a file that isn't there (Day 19)

## How to debug

1. **Run** the code
2. Find the **line number** in the error
3. Read the **type** and **message**: what is Python complaining about?
4. Fix **that one thing** and run again
5. Repeat until it works 🎉

Adding `print()` lines to check what's inside your variables is the oldest (and still one of the best) debugging tricks.

## Your task

The code on the right has **six bugs**, and each is a different error type. Fix them all so the report runs without crashing. Don't change the `ssds` data! When it's fixed it should print:

```
Drives: 4
Last drive: SSD-04
Total GB: 5512
Warehouse capacity: 2000
Drives after restock: 5
```
