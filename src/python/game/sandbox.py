"""Runs a help page's "Try it" example: plain Python, no drone, output captured.

Examples can be edited, so they get a step budget (no infinite loops), capped output,
and may only import math and random."""
import builtins
import io
import sys

from .errors import friendly_error

MAX_OUTPUT = 20_000
MAX_STEPS = 200_000
BLOCKED = {"open", "exec", "eval", "compile", "input", "breakpoint", "exit", "quit", "help"}
ALLOWED_IMPORTS = {"math", "random"}


class TooManySteps(BaseException):
    """BaseException so an example's `except Exception` can't swallow it."""


class CappedOutput(io.StringIO):
    def write(self, text):
        room = MAX_OUTPUT - self.tell()
        if room > 0:
            super().write(text[:room])
        return len(text)


def _import(name, globals=None, locals=None, fromlist=(), level=0):
    if name.split(".")[0] not in ALLOWED_IMPORTS:
        raise ImportError(f"Examples can only import math or random, not {name!r}.")
    return __import__(name, globals, locals, fromlist, level)


def run_snippet(code):
    out = CappedOutput()
    error = None
    steps = 0

    def tracer(frame, event, arg):
        nonlocal steps
        steps += 1
        if steps > MAX_STEPS:
            raise TooManySteps()
        return tracer

    safe = {k: v for k, v in vars(builtins).items() if k not in BLOCKED}
    safe["__import__"] = _import
    safe["print"] = lambda *values, sep=" ", end="\n": out.write(sep.join(str(v) for v in values) + end)
    try:
        compiled = compile(code, "main.py", "exec")
        sys.settrace(tracer)
        try:
            exec(compiled, {"__name__": "__main__", "__builtins__": safe})
        finally:
            sys.settrace(None)
    except TooManySteps:
        error = "Stopped after too many steps. Is there a loop that never ends?"
    except KeyboardInterrupt:
        error = "Stopped."
    except Exception as exc:
        error = friendly_error(exc, {"main.py"})
    return {"stdout": out.getvalue(), "error": error}
