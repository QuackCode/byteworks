SUCCESS = "📦 The warehouse books balance perfectly. Floor 1 is COMPLETE!"


def setup(world):
    rng = world.rng
    inventory = {"DDR3": rng.randint(1, 9), "DDR4": rng.randint(20, 60), "DDR5": rng.randint(20, 60)}
    order = {"model": rng.choice(["DDR4", "DDR5"]), "qty": rng.randint(5, 15)}
    return {"inventory": inventory, "delivery": rng.randint(10, 40), "order": order}


def check(ctx):
    for seed in range(1, 7):
        start = ctx.fresh(seed)
        r = ctx.run(seed=seed)
        ctx.need(r, "retired", "total_sticks", "models")
        inv = dict(start["inventory"])
        inv["DDR5"] += start["delivery"]
        inv["LPDDR5"] = 20
        retired = inv.pop("DDR3")
        order = start["order"]
        inv[order["model"]] -= order["qty"]
        got = r.get("inventory")
        ctx.expect("DDR3" not in got, 'DDR3 is still in the inventory. Remove it with inventory.pop("DDR3").')
        ctx.expect(r.get("retired") == retired, "retired should be the old DDR3 stock, which .pop() gives back.")
        ctx.expect(got.get("LPDDR5") == 20, 'Add the new model: inventory["LPDDR5"] = 20.')
        ctx.expect(got == inv, f"The stock numbers are off. Expected {inv}. Did you add the delivery to DDR5 and take the order from {order['model']}?")
        ctx.expect(r.get("total_sticks") == sum(inv.values()), "total_sticks should add up all the values. Try sum(inventory.values()).")
        ctx.expect(r.get("models") == list(inv.keys()), "models should be a list of the keys. Try list(inventory.keys()).")
        if seed == 1:
            ctx.show("display", text=f"{sum(inv.values())} sticks in stock")
