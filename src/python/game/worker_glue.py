"""What the Pyodide worker calls. Holds the one World for this browser tab.

`bw_bridge` is a JavaScript module the worker registers before importing this file:
    bw_bridge.pace(ms)              block for ms of real time (already divided by drone speed)
    bw_bridge.state(json, anim_ms)  post the world to the page for drawing
    bw_bridge.out(text)             post a console line
"""
import json
import time

import bw_bridge

from . import sandbox, skins, unlocks
from .runner import run_program
from .world import World

WORLD = None
_last_post = 0.0
POST_EVERY = 1 / 60   # never flood the page with more than ~60 redraws per second
PRINT_EVERY = 0.05    # console lines are sent in batches
MAX_BUFFERED = 200    # a print flood keeps only the newest lines
_prints = []
_skipped = 0
_last_print = 0.0


def _state():
    state = WORLD.to_state()
    state["cursor"] = WORLD.cursor      # which line is running (for the editor highlight)
    return json.dumps(state)


def _changed(anim_ms):
    global _last_post
    now = time.monotonic()
    if anim_ms == 0 or now - _last_post >= POST_EVERY:
        _last_post = now
        bw_bridge.state(_state(), anim_ms)


def _out(text):
    global _skipped
    _prints.append(text)
    if len(_prints) > MAX_BUFFERED:
        del _prints[0]
        _skipped += 1
    if time.monotonic() - _last_print >= PRINT_EVERY:
        _flush_prints()


def _flush_prints():
    global _skipped, _last_print
    if _prints or _skipped:
        lines = ([f"…({_skipped} lines skipped)"] if _skipped else []) + _prints
        bw_bridge.out("\n".join(lines))
        _prints.clear()
        _skipped = 0
    _last_print = time.monotonic()


def init(state_json):
    """Start from a saved world. A save that can't be read starts a fresh world and says so."""
    global WORLD
    ok = True
    if state_json:
        try:
            WORLD, ok = World.load(json.loads(state_json))
        except ValueError:
            WORLD, ok = World(seed=1), False
    else:
        WORLD = World(seed=int(time.time()) % 1_000_000)
    return json.dumps({"state": WORLD.to_state(), "warning": not ok})


def new_game():
    global WORLD
    WORLD = World(seed=int(time.time()) % 1_000_000)
    return _state()


def run(files_json, entry):
    result = run_program(WORLD, json.loads(files_json), entry,
                         pace=bw_bridge.pace, on_change=_changed, on_print=_out)
    _flush_prints()
    result["state"] = WORLD.to_state()
    return json.dumps(result)


def buy(unlock_id):
    ok, message = unlocks.buy(WORLD, unlock_id)
    return json.dumps({"ok": ok, "message": message, "state": WORLD.to_state()})


def buy_skin(skin_id):
    ok, message = skins.buy(WORLD, skin_id)
    return json.dumps({"ok": ok, "message": message, "state": WORLD.to_state()})


def skin_list():
    return json.dumps(skins.skins_json())


def tree():
    return json.dumps(unlocks.tree_json())


def snippet(code):
    return json.dumps(sandbox.run_snippet(code))
