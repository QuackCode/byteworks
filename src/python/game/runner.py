"""Run the player's program: check what's unlocked, give it the drone API, and explain any errors."""
import builtins
import types

from .api import Api, StopRun
from .errors import friendly_error
from .gating import ALLOWED_STDLIB, FORBIDDEN, check

MAX_PROBLEMS = 6


class GateError(Exception):
    """A code window imported by the program uses something locked."""


def run_program(world, files, entry="main.py", pace=None, on_change=None, on_print=None, max_ticks=None):
    if entry not in files:
        return {"ok": False, "stopped": False, "error": f"There's no code window called {entry}."}
    user_modules = {name[:-3] for name in files if name.endswith(".py") and name != entry}
    problems = check(files[entry], world.unlocks, entry, user_modules)
    if problems:
        return {"ok": False, "stopped": False, "error": "\n".join(problems[:MAX_PROBLEMS])}

    api = Api(world, pace, on_change, on_print, max_ticks)
    safe_builtins = {k: v for k, v in vars(builtins).items() if k not in FORBIDDEN}
    loaded = {}

    def gated_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name in ALLOWED_STDLIB:
            return __import__(name)
        if name not in user_modules:
            raise ModuleNotFoundError(f"No code window called {name!r}")
        if name not in loaded:
            filename = f"{name}.py"
            found = check(files[filename], world.unlocks, filename, user_modules)
            if found:
                raise GateError("\n".join(found[:MAX_PROBLEMS]))
            module = types.ModuleType(name)
            module.__dict__.update(api.namespace())
            module.__dict__["__builtins__"] = safe_builtins
            loaded[name] = module
            exec(compile(files[filename], filename, "exec"), module.__dict__)
        return loaded[name]

    safe_builtins["__import__"] = gated_import
    safe_builtins["print"] = api.print
    namespace = api.namespace()
    namespace.update(__builtins__=safe_builtins, __name__="__main__")
    user_files = {entry} | {f"{m}.py" for m in user_modules}
    try:
        exec(compile(files[entry], entry, "exec"), namespace)
        return {"ok": True, "stopped": False}
    except (KeyboardInterrupt, StopRun):
        return {"ok": True, "stopped": True}
    except GateError as exc:
        return {"ok": False, "stopped": False, "error": str(exc)}
    except Exception as exc:  # the player's program crashed: explain it kindly
        return {"ok": False, "stopped": False, "error": friendly_error(exc, user_files)}
    finally:
        if on_change:
            on_change(0)
