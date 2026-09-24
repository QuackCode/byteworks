SUCCESS = "📊 Head office approves the numbers. Production lines funded!"


def setup(world):
    rng = world.rng
    return {
        "parts_per_hour": rng.randint(20, 60),
        "hours": rng.randint(6, 12),
        "cost_per_part": rng.choice([1.5, 2.25, 3.0, 3.75]),
        "budget": rng.randint(600, 1600),
        "is_powered": rng.random() < 0.7,
    }


def check(ctx):
    for seed in range(1, 7):
        r = ctx.run(seed=seed)
        ctx.need(r, "total_parts", "total_cost", "boxes", "leftover", "over_budget", "can_run")
        pph, hours, cost = r.get("parts_per_hour"), r.get("hours"), r.get("cost_per_part")
        budget, powered = r.get("budget"), r.get("is_powered")
        total = pph * hours
        ctx.expect(r.get("total_parts") == total, f"total_parts is wrong: with {pph} parts/hour for {hours} hours it should be {total}.")
        ctx.expect(abs(r.get("total_cost") - total * cost) < 1e-9, "total_cost should be total_parts multiplied by cost_per_part.")
        ctx.expect(r.get("boxes") == total // 12, f"boxes should be how many FULL boxes of 12 fit into {total} parts. Try //.")
        ctx.expect(r.get("leftover") == total % 12, "leftover should be the remainder after packing boxes of 12. Try %.")
        over = total * cost > budget
        ctx.expect(r.get("over_budget") is over, "over_budget should be True when total_cost is greater than budget, otherwise False. Use a comparison.")
        ctx.expect(r.get("can_run") is (powered and not over),
                   "can_run should be True only when is_powered is True AND the factory is NOT over budget.")
        if seed == 1:
            ctx.show("display", text=f"{total} parts · {total // 12} boxes · £{total * cost:.2f}")
