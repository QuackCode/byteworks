"""Drone skins: purely cosmetic, and deliberately overpriced."""
from dataclasses import dataclass


@dataclass
class Skin:
    id: str
    name: str
    cost: dict
    blurb: str


SKINS = [
    Skin("classic", "Factory Classic", {}, "The trusty amber workhorse. Free, and proud of it."),
    Skin("pink", "Hot Pink", {"CPU": 2500}, "Loud, fast, fabulous. Costs a small CPU fortune."),
    Skin("ocean", "Ocean", {"SSD": 1500}, "Cool teal with a calm white eye."),
    Skin("stealth", "Stealth", {"RAM": 5000}, "Matte black with a menacing red eye. Nobody will see it coming."),
    Skin("toxic", "Toxic", {"BOARD": 800}, "Neon green. Glows slightly. Probably fine."),
    Skin("rgb", "RGB Gamer", {"GPU": 400}, "Every colour, all the time. Adds zero frames per second."),
    Skin("gold", "Solid Gold", {"COMPUTER": 25}, "More computers than it takes to win. Worth it."),
]
BY_ID = {s.id: s for s in SKINS}
FREE = {s.id for s in SKINS if not s.cost}


def buy(world, skin_id):
    skin = BY_ID.get(skin_id)
    if skin is None:
        return False, f"There's no skin called {skin_id!r}."
    if skin_id in world.skins:
        return False, f"You already own {skin.name}."
    short = {p: n - world.inventory.get(p, 0) for p, n in skin.cost.items() if world.inventory.get(p, 0) < n}
    if short:
        return False, "Not enough parts: need " + ", ".join(f"{n:,} more {p}" for p, n in short.items()) + "."
    for p, n in skin.cost.items():
        world.inventory[p] -= n
    world.skins.add(skin_id)
    return True, f"You bought {skin.name}! Your drone is wearing it now."


def skins_json():
    return [{"id": s.id, "name": s.name, "cost": s.cost, "blurb": s.blurb} for s in SKINS]
