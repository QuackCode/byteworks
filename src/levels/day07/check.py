SUCCESS = "🔍 Scanner fixed and suppliers compared. Head office is impressed!"

MODELS = ["DDR3", "DDR4", "DDR5", "LPDDR4", "LPDDR5", "ECC-DDR5", "SO-DIMM"]


def setup(world):
    rng = world.rng
    sticks = [world.serial("RAM") for _ in range(rng.randint(6, 10))]
    scanned = sticks + rng.sample(sticks, rng.randint(1, 4))
    rng.shuffle(scanned)
    return {
        "scanned": scanned,
        "supplier_a": set(rng.sample(MODELS, 4)),
        "supplier_b": set(rng.sample(MODELS, 4)),
    }


def check(ctx):
    for seed in range(1, 7):
        r = ctx.run(seed=seed)
        ctx.need(r, "unique", "duplicates", "in_both", "all_models", "only_a", "a_sells_ddr5")
        scanned, a, b = r.get("scanned"), r.get("supplier_a"), r.get("supplier_b")
        ctx.expect(isinstance(r.get("unique"), set), "unique should be a set. Try set(scanned).")
        ctx.expect(r.get("unique") == set(scanned), "unique should contain every different serial from scanned.")
        ctx.expect(r.get("duplicates") == len(scanned) - len(set(scanned)),
                   "duplicates should be how many extra scans there were: the list's length minus the set's length.")
        ctx.expect(r.get("in_both") == a & b, "in_both should be the models BOTH suppliers sell (intersection, &).")
        ctx.expect(r.get("all_models") == a | b, "all_models should be every model from either supplier (union, |).")
        ctx.expect(r.get("only_a") == a - b, "only_a should be the models in supplier_a but NOT supplier_b (difference, -).")
        ctx.expect(r.get("a_sells_ddr5") is ("DDR5" in a), 'a_sells_ddr5 should be True/False: is "DDR5" in supplier_a?')
        if seed == 1:
            seen = set()
            for s in scanned:
                ctx.show("part", label=s, result="reject" if s in seen else "ship")
                seen.add(s)
