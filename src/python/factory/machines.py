"""Machines the player's code controls. Each one checks it's used correctly and explains mistakes."""
from .core import FactoryError


def make_cpu(world, dead=False, hot=False):
    rng = world.rng
    return {
        "serial": world.serial("CPU"),
        "clock_ghz": 0.0 if dead else rng.choice([2.1, 2.8, 3.2, 3.6, 4.0, 4.4, 5.0]),
        "temp_c": rng.randint(101, 120) if hot else rng.randint(40, 85),
    }


class Press:
    """Stamps out one CPU per power cycle. Stamping with no power left is an error."""

    def __init__(self, chips):
        self._chips = list(chips)
        self.stamped = 0

    def has_power(self):
        return self.stamped < len(self._chips)

    def stamp(self):
        if not self.has_power():
            raise FactoryError("The press is out of power! Check press.has_power() before stamping.")
        chip = self._chips[self.stamped]
        self.stamped += 1
        return dict(chip)

    def __repr__(self):
        return f"<CPU press: {len(self._chips) - self.stamped} cycles of power left>"


def make_ssd(world, dead=None):
    rng = world.rng
    if dead is None:
        dead = rng.random() < 0.3
    return {
        "serial": world.serial("SSD"),
        "gb": rng.choice([256, 512, 1000, 2000, 4000]),
        "health": rng.randint(0, 19) if dead else rng.randint(20, 100),
    }


def make_board(world, fault=None):
    """fault: None, "blown" (ValueError when installed) or "no_bios" (KeyError when installed)."""
    rng = world.rng
    board = {"serial": world.serial("MB"), "socket": rng.choice(["AM5", "LGA1851"]), "volts": round(rng.uniform(1.0, 1.3), 2)}
    if fault == "blown":
        board["volts"] = round(rng.uniform(1.6, 2.4), 2)
    if fault != "no_bios":
        board["bios"] = f"v{rng.randint(1, 9)}.{rng.randint(0, 9)}"
    return board


class BoardTester:
    """Installs motherboards. Faulty boards raise errors, just like real hardware 'raises' smoke."""

    def __init__(self):
        self.installed = []

    def install(self, board):
        if board["volts"] > 1.5:
            raise ValueError(f"{board['serial']} blew a capacitor at {board['volts']}V!")
        bios = board["bios"]  # KeyError if the BIOS chip is missing
        self.installed.append(board["serial"])
        return f"{board['serial']} installed (BIOS {bios})"
