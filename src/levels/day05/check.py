SUCCESS = "🧠 The RAM conveyor hums along. Every stick in its place!"


def setup(world):
    rng = world.rng
    belt = [world.serial("RAM") for _ in range(rng.randint(5, 8))]
    rng.shuffle(belt)
    faulty = rng.choice(belt[1:])
    return {"belt": belt, "new_stick": world.serial("RAM"), "faulty_stick": faulty}


def check(ctx):
    for seed in range(1, 6):
        start = ctx.fresh(seed)
        r = ctx.run(seed=seed)
        ctx.need(r, "tester", "count", "first_on_belt", "last_on_belt")
        expected = list(start["belt"])
        expected.append(start["new_stick"])
        ctx.expect(start["new_stick"] in r.get("belt"), "The new stick isn't on the belt. Use belt.append(new_stick).")
        ctx.expect(start["faulty_stick"] not in r.get("belt"), "The faulty stick is still on the belt! Use belt.remove(faulty_stick).")
        expected.remove(start["faulty_stick"])
        tester = expected.pop(0)
        ctx.expect(r.get("tester") == tester, f"tester should be the FIRST stick on the belt ({tester}). Use belt.pop(0) after steps 1 and 2.")
        expected.sort()
        ctx.expect(r.get("belt") == expected, f"The belt should end up sorted: {expected}. Did you use belt.sort()?")
        ctx.expect(r.get("count") == len(expected), "count should be how many sticks are on the belt. Use len(belt).")
        ctx.expect(r.get("first_on_belt") == expected[0], "first_on_belt should be belt[0] (after sorting).")
        ctx.expect(r.get("last_on_belt") == expected[-1], "last_on_belt should be belt[-1] (after sorting).")
        if seed == 1:
            ctx.show("part", label=start["faulty_stick"], result="reject")
            for stick in expected:
                ctx.show("part", label=stick, result="ship")
