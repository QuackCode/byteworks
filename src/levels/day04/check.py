SUCCESS = "🏷️ The label printer whirrs. Perfect labels, every time!"


def setup(world):
    rng = world.rng
    kind = rng.choice(["ram", "cpu", "gpu", "ssd"])
    num = rng.randint(1, 9999)
    left = " " * rng.randint(1, 4)
    right = " " * rng.randint(1, 4)
    return {"raw_code": f"{left}{kind}-{num:04d}{right}"}


def check(ctx):
    for seed in range(1, 9):
        r = ctx.run(seed=seed)
        ctx.need(r, "clean", "part_type", "number", "label", "sku", "is_ram")
        raw = r.get("raw_code")
        clean = raw.strip().upper()
        ctx.expect(r.get("clean") == clean, f"For {raw!r}, clean should be {clean!r}. Strip the spaces AND make it uppercase.")
        ctx.expect(r.get("part_type") == clean[:3], f"part_type should be the first 3 characters: {clean[:3]!r}.")
        ctx.expect(r.get("number") == clean[-4:], f"number should be the last 4 characters: {clean[-4:]!r}.")
        label = f"{clean[:3]} #{clean[-4:]}"
        ctx.expect(r.get("label") == label, f"label should look like {label!r}: type, a space, #, then the number.")
        ctx.expect(label in r.lines, "Don't forget to print(label)!")
        ctx.expect(r.get("sku") == clean.replace("-", ""), f"sku should be clean without the dash: {clean.replace('-', '')!r}.")
        ctx.expect(r.get("is_ram") is clean.startswith("RAM"), "is_ram should be True only when clean starts with 'RAM'. Try .startswith().")
        if seed == 1:
            ctx.show("display", text=label)
