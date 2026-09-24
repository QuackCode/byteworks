"""Turn Python exceptions into beginner-friendly messages that point at the player's own line."""
import traceback

EXPLAIN = {
    "SyntaxError": "Python couldn't read this line. Look for a missing bracket, quote or colon (:).",
    "IndentationError": "The spacing at the start of this line is wrong. Code inside if/while/for/def must be indented by 4 spaces.",
    "NameError": "Python doesn't know that name. Check the spelling, or make sure you created it before using it.",
    "TypeError": "You mixed up types, e.g. adding a number to a string, or calling something the wrong way.",
    "ValueError": "The type was right but the value wasn't.",
    "IndexError": "You asked for a position that doesn't exist in the list. Remember: counting starts at 0.",
    "KeyError": "That key isn't in the dictionary. Check the spelling and capital letters.",
    "AttributeError": "That thing doesn't have the method or attribute you asked for.",
    "ZeroDivisionError": "You divided by zero. Even a factory can't do that!",
    "RecursionError": "A function kept calling itself forever.",
    "ModuleNotFoundError": "There's no code window with that name. Check the spelling (no .py in the import).",
    "FaultyBoardError": "You harvested a faulty motherboard! Check is_faulty() first and replace faulty boards with place(Part.BOARD). Once you unlock Exceptions you can also catch it with try/except.",
}


def _where(exc, user_files):
    """(file, line) of the deepest frame that belongs to the player's code."""
    if isinstance(exc, SyntaxError) and exc.filename in user_files:
        return exc.filename, exc.lineno
    found = (None, None)
    for frame, lineno in traceback.walk_tb(exc.__traceback__):
        if frame.f_code.co_filename in user_files:
            found = (frame.f_code.co_filename, lineno)
    return found


def friendly_error(exc, user_files):
    name = type(exc).__name__
    file, line = _where(exc, user_files)
    if line is None:
        where = ""
    elif file == "main.py" or len(user_files) == 1:
        where = f"Line {line}: "
    else:
        where = f"{file} line {line}: "
    detail = exc.msg if isinstance(exc, SyntaxError) else str(exc)
    return f"{where}{name}: {detail}\n{EXPLAIN.get(name, '')}".strip()
