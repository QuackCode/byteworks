## The problem: one Python, many projects

Imagine two projects on your computer:

- **Project A** needs `rgbglow` version **0.9** (newer versions broke it)
- **Project B** needs `rgbglow` version **1.3** (it uses new features)

`pip install` puts packages into your **one** Python installation, so only one version can be installed at a time. Install 1.3 and Project A breaks. Install 0.9 and Project B breaks. 😩

## The fix: virtual environments

A **virtual environment** (venv) is a private, sealed folder with its **own** Python and its **own** packages. Each project gets one, so they can never clash.

On a real computer, in a terminal, inside your project folder:

```
python -m venv venv             # create an environment in a folder called venv
source venv/bin/activate        # switch to it (Mac/Linux)
venv\Scripts\activate           # switch to it (Windows)
pip install rgbglow==0.9        # installs ONLY into this venv
pip freeze > requirements.txt   # record exactly what this project needs
deactivate                      # switch back to the normal Python
```

While a venv is active, your terminal prompt shows its name, like `(venv) $`.

## Good habits

- **One venv per project**, created in the project folder
- **Never share the venv folder** (don't upload it to GitHub: add it to `.gitignore`). Share `requirements.txt` instead
- Anyone can rebuild your setup with `pip install -r requirements.txt` inside their own new venv

## venvs in ByteWorks

The factory gives you a `venv` manager that works the same way:

| Terminal | ByteWorks |
|---|---|
| `python -m venv gpu-render` | `render = venv.create("gpu-render")` |
| `pip install rgbglow==0.9` (while active) | `render.install("rgbglow==0.9")` |
| `source gpu-render/bin/activate` | `venv.activate("gpu-render")` |
| `pip freeze` | `render.freeze()` |

## Your task

1. Create an environment `gpu-render` (store it in `render`) and install `rgbglow==0.9` **and** `boardcheck==2.1` into it
2. Create an environment `gpu-tester` (store it in `tester`) and install `rgbglow==1.3` into it
3. **Activate** `gpu-tester`, `import rgbglow`, and store `rgbglow.__version__` in `tester_version`
4. For **each** environment, write its `freeze()` text into a file called `<env name>-requirements.txt`, e.g. `gpu-render-requirements.txt`
