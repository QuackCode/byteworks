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


GOOD_RAM = (32, 5600)


class Warehouse:
    """Hands out parts from every floor. Around a third of them are faulty in some way."""

    KINDS = ("cpu", "ram", "ssd", "motherboard", "gpu")
    MAX_FETCHES = 300

    def __init__(self, world):
        self.world = world
        self.registry = {}   # serial -> (kind, original part)
        self.fetches = 0
        self.scrapped = []

    def _make(self, kind):
        w, rng = self.world, self.world.rng
        bad = rng.random() < 0.35
        if kind == "cpu":
            return make_cpu(w, dead=bad and rng.random() < 0.5, hot=bad and rng.random() < 0.5)
        if kind == "ram":
            spec = rng.choice([(16, 4800), (31, 5600), (32, 4800)]) if bad else GOOD_RAM
            return {"serial": w.serial("RAM"), "spec": spec}
        if kind == "ssd":
            return make_ssd(w, dead=bad)
        if kind == "motherboard":
            return make_board(w, fault=rng.choice(["blown", "no_bios"]) if bad else None)
        score = round(rng.uniform(1500, 4999), 0) if bad else round(rng.uniform(5000, 12000), 0)
        return {"serial": w.serial("GPU"), "score": score}

    def fetch(self, kind):
        if kind not in self.KINDS:
            raise FactoryError(f"The warehouse has no {kind!r}. Try one of: {', '.join(self.KINDS)}")
        self.fetches += 1
        if self.fetches > self.MAX_FETCHES:
            raise FactoryError("The warehouse is empty! Is a loop fetching parts forever? Check your tests return True for good parts.")
        part = self._make(kind)
        self.registry[part["serial"]] = (kind, dict(part))
        return dict(part)

    def scrap(self, part):
        self.scrapped.append(part["serial"])

    def __repr__(self):
        return f"<warehouse: {self.fetches} parts fetched, {len(self.scrapped)} scrapped>"
