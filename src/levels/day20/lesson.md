## Packages: code other people wrote for you

Python's standard library is big, but the **Python Package Index** ([pypi.org](https://pypi.org)) has **over half a million** more packages, free for anyone to use: `requests` for the web, `numpy` for maths, `pandas` for data, `flask` for websites… You'll use some of these in the next few days!

## `pip`: the package installer

**pip** downloads and installs packages. On a real computer you type these commands in a **terminal** (not in Python):

```
pip install requests            # latest version
pip install requests==2.31.0    # a specific version
pip list                        # what's installed?
pip show requests               # details about one package
pip uninstall requests          # remove it
pip freeze > requirements.txt   # save your exact setup to a file
pip install -r requirements.txt # rebuild that setup somewhere else
```

After installing, you `import` a package just like a standard-library module.

## `requirements.txt`

Projects list their packages in a `requirements.txt` file, one `name==version` per line:

```
flask==3.0.0
requests==2.31.0
```

Anyone can then run `pip install -r requirements.txt` to get exactly the same setup. **Pinning** versions with `==` means an update can't break your code by surprise.

## Making your own package

A **package** is a folder of modules with a special file called `__init__.py` inside:

```
cpu_tools/
    __init__.py     # makes the folder a package (can be empty)
    grading.py
    pricing.py
```

Then: `from cpu_tools.grading import grade`. That's exactly how `factory.cpu_tools` works in ByteWorks!

## pip in ByteWorks

Your code runs inside your web browser, where a real terminal isn't available, so the factory gives you a `pip` object that works the same way:

| Terminal | ByteWorks |
|---|---|
| `pip install boardcheck==2.1` | `pip.install("boardcheck==2.1")` |
| `pip uninstall rgbglow` | `pip.uninstall("rgbglow")` |
| `pip list` | `pip.list()` |
| `pip freeze` | `pip.freeze()` (gives back the text) |

## Your task

You're given `boards` (a list of motherboard dicts) and `pip`.

1. Install version `2.1` of `boardcheck`
2. `import boardcheck`
3. `results`: a dict of **serial → `boardcheck.scan(board)`** for every board
4. Install `rgbglow`, then change your mind and **uninstall** it
5. Write `pip.freeze()` into a file called `requirements.txt`
