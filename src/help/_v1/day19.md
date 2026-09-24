## Files: remembering things after the program ends

Variables vanish when your program stops. **Files** stay. Python can read and write them with `open()`.

(ByteWorks gives your code its own private folder, so experiment freely!)

## Writing a text file

```python
with open("notes.txt", "w") as f:
    f.write("Line one\n")
    f.write("Line two\n")
print("Saved!")
```

- `"w"` = **write**: creates the file, or **replaces** it if it already exists
- `"a"` = **append**: adds to the end
- `"r"` = **read** (the default)
- `\n` = a new line (`write` doesn't add one for you)

`with` automatically **closes** the file when the block ends, even if there's an error. Always use it.

## Reading a text file

```python
with open("notes.txt", "w") as f:
    f.write("alpha\nbeta\ngamma\n")

with open("notes.txt") as f:
    text = f.read()               # the whole file as one string
print(text)
print(text.splitlines())          # a list of lines, without the \n

with open("notes.txt") as f:
    for line in f:                # or loop line by line
        print("->", line.strip())
```

## JSON: dicts and lists in a file

**JSON** is the most common format for sharing data between programs. It looks almost exactly like Python dicts and lists:

```python
import json
spec = {"socket": "AM5", "slots": 4, "wifi": True}
with open("spec.json", "w") as f:
    json.dump(spec, f)              # Python → file

with open("spec.json") as f:
    loaded = json.load(f)           # file → Python
print(loaded["socket"])
print(json.dumps(spec))             # Python → JSON text
```

## CSV: spreadsheets

**CSV** (comma-separated values) is how spreadsheets are saved as plain text:

```python
import csv
with open("tests.csv", "w") as f:
    f.write("serial,status\nMB-1,PASS\nMB-2,FAIL\n")

with open("tests.csv") as f:
    rows = list(csv.DictReader(f))   # each row becomes a dict using the header line
print(rows)
print(rows[0]["status"])
```

## Checking and deleting files with `os`

```python
import os
print(os.path.exists("tests.csv"))
print(os.listdir())
```

`os.remove("name")` deletes a file.

## Your task

Your folder contains `orders.txt` (one order per line), `specs.json` and `boards.csv` (columns `serial`, `status`).

1. `orders`: a **list** of the lines in `orders.txt`
2. `socket`: the `"socket"` value from `specs.json`
3. `rows`: a list of dicts from `boards.csv`
4. `passed`: the serial of every row whose `status` is `"PASS"`
5. Write `production.log` with one line `BUILT <order>` for each order
6. Then **append** a final line `SHIFT END` to it
7. `log_exists`: use `os.path.exists` to confirm `production.log` exists
