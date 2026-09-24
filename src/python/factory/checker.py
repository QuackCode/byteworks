"""Runs a player's code against a level's check script and explains the result kindly.

A level's check.py defines:
    setup(world)  -> dict of names the player's code starts with (belts, machines, data)
    check(ctx)    -> uses ctx.run(seed) and ctx.expect(...) to test the player's code
"""
import contextlib
import io
import json
import sys
import traceback

from .core import FactoryError, world

USER_FILE = "<your code>"
MAX_OUTPUT = 20_000
BLANK = "____"


class CheckFailed(Exception):
    pass


def _user_line(exc):
    if isinstance(exc, SyntaxError) and exc.filename == USER_FILE:
        return exc.lineno
    line = None
    for frame, lineno in traceback.walk_tb(exc.__traceback__):
        if frame.f_code.co_filename == USER_FILE:
            line = lineno
    return line


EXPLAIN = {
    "SyntaxError": "Python couldn't read this line. Look for a missing bracket, quote or colon (:).",
    "IndentationError": "The spacing at the start of this line is wrong. Code inside if/while/for/def must be indented by 4 spaces.",
    "NameError": "Python doesn't know that name. Check the spelling, or make sure you created it before using it.",
    "TypeError": "You mixed up types, e.g. adding a number to a string, or calling something the wrong way.",
    "ValueError": "The type was right but the value wasn't, e.g. int('abc').",
    "IndexError": "You asked for a position that doesn't exist in the list. Remember: counting starts at 0.",
    "KeyError": "That key isn't in the dictionary. Check the spelling and capital letters.",
    "AttributeError": "That thing doesn't have the method or attribute you asked for.",
    "ZeroDivisionError": "You divided by zero. Even a factory can't do that!",
    "FactoryError": "A machine refused to do that.",
}


def friendly_error(exc):
    name = type(exc).__name__
    line = _user_line(exc)
    where = f"Line {line}: " if line else ""
    if isinstance(exc, NameError) and getattr(exc, "name", None) == BLANK:
        return f"{where}there's still a blank (____) to fill in. Replace it with your own code."
    if isinstance(exc, SyntaxError):
        detail = exc.msg
    else:
        detail = str(exc)
    hint = EXPLAIN.get(name, "")
    return f"{where}{name}: {detail}\n{hint}".strip()


def _make_input(answers):
    answers = list(answers)

    def fake_input(prompt=""):
        print(prompt, end="")
        value = answers.pop(0) if answers else ""
        print(value)
        return value

    return fake_input


class Run:
    def __init__(self, ns, stdout, error, events):
        self.ns = ns
        self.stdout = stdout
        self.error = error
        self.events = events

    @property
    def lines(self):
        return [l.strip() for l in self.stdout.splitlines() if l.strip()]

    def get(self, name, default=None):
        return self.ns.get(name, default)


class Ctx:
    def __init__(self, code, level):
        self.code = code
        self.level = level
        self.first = None
        self.extra_events = []

    def run(self, seed=1, inputs=(), setup_args=None):
        world.reset(seed)
        ns = {"__name__": "__main__", "input": _make_input(inputs)}
        if hasattr(self.level, "setup"):
            ns.update(self.level.setup(world, **(setup_args or {})))
        out = io.StringIO()
        error = None
        try:
            compiled = compile(self.code, USER_FILE, "exec")
            with contextlib.redirect_stdout(out):
                exec(compiled, ns)
        except Exception as exc:  # the player's code crashed: explain it
            error = friendly_error(exc)
        run = Run(ns, out.getvalue()[:MAX_OUTPUT], error, list(world.events))
        if self.first is None:
            self.first = run
        return run

    def fresh(self, seed=1, setup_args=None):
        """The untouched starting values for a seed (the player's run may have changed them)."""
        world.reset(seed)
        values = self.level.setup(world, **(setup_args or {}))
        world.reset(seed)
        return values

    def expect(self, condition, message):
        if not condition:
            raise CheckFailed(message)

    def no_crash(self, run):
        """Fail with the friendly error if the player's code crashed."""
        if run.error:
            raise CheckFailed(run.error)

    def need(self, run, *names):
        self.no_crash(run)
        for name in names:
            if name not in run.ns:
                raise CheckFailed(f"I can't find a variable called `{name}`. Did you create it (spelled exactly like that)?")

    def show(self, type, **data):
        """Add an event for the factory animation."""
        self.extra_events.append({"type": type, **data})


def _load_level(check_src):
    module = type(sys)("level_check")
    exec(compile(check_src, "check.py", "exec"), module.__dict__)
    return module


def run_check(code, check_src):
    level = _load_level(check_src)
    ctx = Ctx(code, level)
    passed, message = True, None
    try:
        level.check(ctx)
    except CheckFailed as exc:
        passed, message = False, str(exc)
    except Exception as exc:  # safety net: a check tripped over unexpected player values
        passed = False
        message = f"Your code ran, but the result wasn't what the factory expected ({type(exc).__name__}: {exc})."
    first = ctx.first
    events = (first.events if first else []) + ctx.extra_events
    return json.dumps({
        "passed": passed,
        "message": message or getattr(level, "SUCCESS", "Shift complete!"),
        "stdout": first.stdout if first else "",
        "error": first.error if first else None,
        "events": events,
    })


def run_snippet(code):
    """Run code from a lesson's "Try it" box: no checks, just output."""
    world.reset(1)
    ns = {"__name__": "__main__", "input": _make_input([])}
    out = io.StringIO()
    error = None
    try:
        compiled = compile(code, USER_FILE, "exec")
        with contextlib.redirect_stdout(out):
            exec(compiled, ns)
    except Exception as exc:
        error = friendly_error(exc)
    return json.dumps({"stdout": out.getvalue()[:MAX_OUTPUT], "error": error})


__all__ = ["run_check", "run_snippet", "FactoryError"]
