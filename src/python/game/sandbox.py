"""Runs a help page's "Try it" example: plain Python, no drone, output captured."""
import contextlib
import io

from .errors import friendly_error

MAX_OUTPUT = 20_000


def run_snippet(code):
    out = io.StringIO()
    error = None
    try:
        compiled = compile(code, "main.py", "exec")
        with contextlib.redirect_stdout(out):
            exec(compiled, {"__name__": "__main__"})
    except Exception as exc:
        error = friendly_error(exc, {"main.py"})
    return {"stdout": out.getvalue()[:MAX_OUTPUT], "error": error}
