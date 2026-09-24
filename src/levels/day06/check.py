SUCCESS = "🔩 The spec plate is bolted on. Nobody's changing THAT!"

STANDARD = (32, 5600)
OTHERS = [(16, 4800), (31, 5600), (32, 4800), (64, 6000), (8, 3200)]


def setup(world):
    rng = world.rng
    specs = [STANDARD] * rng.randint(1, 4) + [rng.choice(OTHERS) for _ in range(rng.randint(3, 6))]
    rng.shuffle(specs)
    return {"specs": specs}


def check(ctx):
    for seed in range(1, 6):
        r = ctx.run(seed=seed)
        ctx.need(r, "STANDARD", "capacity", "speed", "matching", "first_match", "fast_spec")
        ctx.expect(type(r.get("STANDARD")) is tuple, "STANDARD should be a tuple: round brackets, like (32, 5600).")
        ctx.expect(r.get("STANDARD") == STANDARD, "STANDARD should be (32, 5600).")
        ctx.expect((r.get("capacity"), r.get("speed")) == STANDARD, "Unpack STANDARD: capacity, speed = STANDARD.")
        specs = r.get("specs")
        ctx.expect(r.get("matching") == specs.count(STANDARD), "matching should count how many specs equal STANDARD. Try specs.count(...).")
        ctx.expect(r.get("first_match") == specs.index(STANDARD), "first_match should be the position of the first match. Try specs.index(...).")
        ctx.expect(r.get("fast_spec") == (32, 6400) and type(r.get("fast_spec")) is tuple,
                   "fast_spec should be a NEW tuple: (capacity, 6400).")
        if seed == 1:
            for spec in specs:
                ctx.show("part", label=f"{spec[0]}GB {spec[1]}", result="ship" if spec == STANDARD else "reject")
