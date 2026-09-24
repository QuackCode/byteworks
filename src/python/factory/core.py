"""The factory world: seeded randomness plus the event log the website animates."""
import random

MAX_EVENTS = 400


class World:
    def __init__(self):
        self.reset(1)

    def reset(self, seed):
        self.seed = seed
        self.rng = random.Random(seed)
        self.events = []
        self.serial_counter = 0

    def log(self, type, **data):
        if len(self.events) < MAX_EVENTS:
            self.events.append({"type": type, **data})

    def serial(self, prefix):
        self.serial_counter += 1
        return f"{prefix}-{self.rng.randint(0, 99):02d}{self.serial_counter:02d}"


world = World()


class FactoryError(Exception):
    """Raised by machines when the player uses them the wrong way."""
