"""Before a program runs, walk its syntax tree and refuse anything the player hasn't unlocked yet."""
import ast

from .errors import friendly_error
from .unlocks import BY_ID

NODE_FEATURE = {
    ast.While: ("loops", "while loops"), ast.Break: ("loops", "break"), ast.Continue: ("loops", "continue"),
    ast.Assign: ("variables", "variables"), ast.AugAssign: ("variables", "variables"),
    ast.AnnAssign: ("variables", "variables"), ast.BinOp: ("variables", "maths operators"),
    ast.UnaryOp: ("variables", "operators"), ast.Compare: ("variables", "comparisons"),
    ast.BoolOp: ("variables", "and / or"),
    ast.If: ("conditionals", "if statements"), ast.IfExp: ("conditionals", "if expressions"),
    ast.For: ("for_loops", "for loops"),
    ast.FunctionDef: ("functions", "def"), ast.Return: ("functions", "return"),
    ast.Global: ("functions", "global"), ast.Nonlocal: ("functions", "nonlocal"),
    ast.List: ("lists", "lists"), ast.Subscript: ("lists", "[ ] indexing"),
    ast.Tuple: ("positions", "tuples"),
    ast.Dict: ("dicts", "dictionaries"), ast.Set: ("sets", "sets"),
    ast.JoinedStr: ("strings", "f-strings"),
    ast.ListComp: ("comprehensions", "list comprehensions"), ast.SetComp: ("comprehensions", "set comprehensions"),
    ast.DictComp: ("comprehensions", "dict comprehensions"), ast.GeneratorExp: ("comprehensions", "generator expressions"),
    ast.Lambda: ("comprehensions", "lambda"),
    ast.Import: ("modules", "import"), ast.ImportFrom: ("modules", "import"),
    ast.Try: ("exceptions", "try / except"), ast.Raise: ("exceptions", "raise"),
    ast.ClassDef: ("classes", "class"),
}

BUILTIN_UNLOCK = {
    "range": "for_loops", "enumerate": "lists", "zip": "lists", "len": "lists", "list": "lists", "sum": "lists",
    "reversed": "lists", "any": "lists", "all": "lists", "tuple": "positions", "dict": "dicts", "set": "sets",
    "str": "strings", "sorted": "hof", "map": "hof", "filter": "hof", "int": "variables", "float": "variables",
    "abs": "variables", "min": "variables", "max": "variables", "round": "variables", "bool": "variables",
    "type": "variables", "isinstance": "classes", "super": "classes", "Exception": "exceptions",
    "ValueError": "exceptions", "KeyError": "exceptions", "IndexError": "exceptions", "TypeError": "exceptions",
    "ZeroDivisionError": "exceptions",
}

API_UNLOCK = {
    "harvest": None, "move": None, "print": None, "North": None, "East": None, "South": None, "West": None,
    "Part": None, "wait": "loops", "num_items": "variables", "can_harvest": "conditionals",
    "get_part": "conditionals", "place": "floor_cpu", "goto_floor": "floor_cpu", "get_floor": "floor_cpu",
    "Floor": "floor_cpu", "get_pos": "positions", "get_world_size": "positions", "is_faulty": "floor_board",
    "FaultyBoardError": "floor_board", "measure": "floor_gpu", "swap": "floor_gpu", "get_order": "floor_assembly",
    "assemble": "floor_assembly",
}

# BaseException / KeyboardInterrupt / SystemExit are blocked so a program can't swallow the Stop button.
FORBIDDEN = {"open", "exec", "eval", "compile", "__import__", "globals", "locals", "vars", "input", "breakpoint",
             "exit", "quit", "help", "getattr", "setattr", "delattr", "memoryview", "__builtins__",
             "BaseException", "KeyboardInterrupt", "SystemExit"}
ALLOWED_DUNDERS = {"__init__", "__str__", "__repr__", "__name__", "__eq__", "__lt__"}
ALLOWED_STDLIB = {"math", "random"}
UNSUPPORTED = (ast.AsyncFunctionDef, ast.Await, ast.AsyncFor, ast.AsyncWith, ast.Yield, ast.YieldFrom, ast.With)


def _where(filename, line):
    return f"Line {line}" if filename == "main.py" else f"{filename} line {line}"


def _locked(node, what, unlock_id):
    title = BY_ID[unlock_id].title
    return node.lineno, f"you haven't unlocked {what} yet. Find \u201c{title}\u201d in the Upgrades tree."


def check(source, unlocked, filename, user_modules):
    try:
        tree = ast.parse(source, filename)
    except SyntaxError as exc:
        return [friendly_error(exc, {filename})]
    found = set()   # (line, message): the same problem on the same line is reported once
    for node in ast.walk(tree):
        if isinstance(node, UNSUPPORTED):
            found.add((node.lineno, "ByteWorks doesn't support that kind of statement."))
            continue
        feature = NODE_FEATURE.get(type(node))
        if feature and feature[0] not in unlocked:
            found.add(_locked(node, feature[1], feature[0]))
        if isinstance(node, ast.Name):
            name = node.id
            if name in FORBIDDEN:
                found.add((node.lineno, f"{name} isn't available in ByteWorks."))
            elif API_UNLOCK.get(name) and API_UNLOCK[name] not in unlocked:
                found.add(_locked(node, name, API_UNLOCK[name]))
            elif name in BUILTIN_UNLOCK and BUILTIN_UNLOCK[name] not in unlocked:
                found.add(_locked(node, f"{name}()", BUILTIN_UNLOCK[name]))
        elif isinstance(node, ast.ExceptHandler) and node.type is None:
            found.add((node.lineno, "name the error you expect, e.g. except FaultyBoardError: (a bare except: would "
                                    "also catch the Stop button)."))
        elif isinstance(node, ast.Attribute) and node.attr.startswith("__") and node.attr not in ALLOWED_DUNDERS:
            found.add((node.lineno, f"{node.attr} isn't available in ByteWorks."))
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            names = [a.name for a in node.names] if isinstance(node, ast.Import) else [node.module or ""]
            for name in names:
                if name not in ALLOWED_STDLIB and name not in user_modules:
                    found.add((node.lineno, f"you can only import math, random or your own code windows, not {name!r}."))
    return [f"{_where(filename, line)}: {msg}" for line, msg in sorted(found)]
