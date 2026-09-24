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
