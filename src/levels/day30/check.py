import json

from factory.cpu_tools import grade
from factory.machines import GOOD_RAM, BoardTester, Warehouse

SUCCESS = ("🏆 EVERY ORDER SHIPPED, ZERO FAULTS. ByteWorks is back in business, and you learned Python doing it. "
           "Foreman Flo is framing your first Factory online printout. Congratulations, engineer! 🎉")

KEYS = ["order", "cpu", "ram", "ssd", "motherboard", "gpu"]


def setup(world):
    rng = world.rng
    orders = [{"id": i, "type": rng.choice(["GAMING", "OFFICE"])} for i in range(1, rng.randint(4, 7))]
    orders[0]["type"], orders[1]["type"] = "GAMING", "OFFICE"
    return {"orders": orders, "warehouse": Warehouse(world), "tester": BoardTester()}


def part_ok(kind, part, order_type):
    gaming = order_type == "GAMING"
    if kind == "cpu":
        return grade(part) == "GAMING" if gaming else grade(part) != "REJECT"
    if kind == "ram":
        return tuple(part["spec"]) == GOOD_RAM
    if kind == "ssd":
        return part["health"] >= 20
    if kind == "motherboard":
        return part["volts"] <= 1.5 and "bios" in part
    return part["score"] >= (8000 if gaming else 5000)


def why_bad(kind, part, order_type):
    if kind == "cpu":
        return f"CPU {part['serial']} grades {grade(part)}, which isn't allowed in a {order_type} order"
    if kind == "ram":
        return f"RAM {part['serial']} has spec {part['spec']}, not (32, 5600)"
    if kind == "ssd":
        return f"SSD {part['serial']} only has {part['health']}% health"
    if kind == "motherboard":
        return f"motherboard {part['serial']} is faulty (tester.install raises an error)"
    need = 8000 if order_type == "GAMING" else 5000
    return f"GPU {part['serial']} only scores {part['score']:.0f} (a {order_type} order needs {need}+)"


def check(ctx):
    for seed in range(1, 6):
        r = ctx.run(seed=seed)
        ctx.need(r, "fetch_good", "board_ok", "computers")
        orders, wh = r.get("orders"), r.get("warehouse")
        computers = r.get("computers")
        ctx.expect(len(computers) == len(orders), f"There are {len(orders)} orders but you built {len(computers)} computers.")
        used = set()
        types = {o["id"]: o["type"] for o in orders}
        for comp, order in zip(computers, orders):
            ctx.expect(isinstance(comp, dict) and list(comp) == KEYS,
                       f"Each computer should be a dict with the keys {KEYS} (in that order).")
            ctx.expect(comp["order"] == order["id"], "Build the computers in the same order as the orders list.")
            for kind in KEYS[1:]:
                serial = comp[kind]
                ctx.expect(serial in wh.registry and wh.registry[serial][0] == kind,
                           f"Order {order['id']}'s {kind} should be the serial of a {kind} from the warehouse.")
                ctx.expect(serial not in used, f"Part {serial} was used in two computers!")
                used.add(serial)
                part = wh.registry[serial][1]
                ctx.expect(part_ok(kind, part, types[order["id"]]),
                           f"Order {order['id']} ({order['type']}) shipped a bad part: {why_bad(kind, part, order['type'])}.")
        bad_fetched = [s for s, (kind, part) in wh.registry.items() if s not in used and not part_ok(kind, part, "OFFICE")]
        unscrapped = [s for s in bad_fetched if s not in wh.scrapped]
        ctx.expect(not unscrapped, f"Faulty parts weren't sent back: {unscrapped[:3]}. Call warehouse.scrap(part) on every bad part.")
        ctx.expect(json.loads(r.files.get("shipped.json", "null") or "null") == computers,
                   'Save computers to shipped.json: with open("shipped.json", "w") as f: json.dump(computers, f)')
        if seed == 1:
            for serial in list(wh.registry)[:14]:
                ctx.show("part", label=serial, result="reject" if serial in wh.scrapped else "ship")
            for comp in computers:
                ctx.show("part", label=f"PC #{comp['order']}", result="ship")
