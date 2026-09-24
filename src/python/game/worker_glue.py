"""What the Pyodide worker calls. Holds the one World for this browser tab.

`bw_bridge` is a JavaScript module the worker registers before importing this file:
    bw_bridge.pace(ms)              block for ms of real time (already divided by drone speed)
    bw_bridge.state(json, anim_ms)  post the world to the page for drawing
    bw_bridge.out(text)             post a console line
"""
import json
import time

import bw_bridge

from . import sandbox, unlocks
from .runner import run_program
from .world import World

WORLD = None
_last_post = 0.0
POST_EVERY = 1 / 60   # never flood the page with more than ~60 redraws per second


def _state():
    return json.dumps(WORLD.to_state())


def _changed(anim_ms):
    global _last_post
    now = time.monotonic()
    if anim_ms == 0 or now - _last_post >= POST_EVERY:
        _last_post = now
        bw_bridge.state(_state(), anim_ms)


def init(state_json):
    global WORLD
    WORLD = World.from_state(json.loads(state_json)) if state_json else World(seed=int(time.time()) % 1_000_000)
    return _state()


def new_game():
    global WORLD
    WORLD = World(seed=int(time.time()) % 1_000_000)
    return _state()


def run(files_json, entry):
    result = run_program(WORLD, json.loads(files_json), entry,
                         pace=bw_bridge.pace, on_change=_changed, on_print=bw_bridge.out)
    result["state"] = WORLD.to_state()
    return json.dumps(result)


def buy(unlock_id):
    ok, message = unlocks.buy(WORLD, unlock_id)
    return json.dumps({"ok": ok, "message": message, "state": WORLD.to_state()})


def tree():
    return json.dumps(unlocks.tree_json())


def snippet(code):
    return json.dumps(sandbox.run_snippet(code))
