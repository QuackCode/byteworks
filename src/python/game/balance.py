"""Every number that decides how ByteWorks feels. Tune here, and nowhere else."""

MS_PER_TICK = 2          # real milliseconds per game tick at speed x1 (a 100-tick move = 0.2 s)
START_SIZE = 3
MAX_SIZE = 8

ACTION_TICKS = {
    "harvest": 100, "move": 100, "place": 100, "swap": 100,
    "print": 50, "goto_floor": 400, "assemble": 200, "sense": 1,
}

# (min, max) ticks for a part to become ready after it is planted / harvested
GROW_TICKS = {"RAM": (250, 350), "CPU": (1200, 2000), "SSD": (1800, 2600), "BOARD": (2500, 3500), "GPU": (800, 1200)}

PLACE_COST = {"CPU": {}, "SSD": {"RAM": 3, "CPU": 1}, "BOARD": {"SSD": 2}, "GPU": {"BOARD": 1, "CPU": 2}}
YIELD = {"RAM": 1, "CPU": 1, "SSD": 2, "BOARD": 1, "GPU": 1}
FAULT_CHANCE = 0.2

# Real-time speed multiplier for each Speed upgrade level (index = level)
SPEEDS = [1, 1.5, 2, 3, 4, 6]

# Final Assembly orders: base quantity per part, scaled up as more orders are completed
ORDER_BASE = {"RAM": 20, "CPU": 10, "SSD": 8, "BOARD": 4, "GPU": 4}
WIN_COMPUTERS = 10
