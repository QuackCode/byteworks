from datetime import datetime, timedelta

SUCCESS = "⏰ The shift clock ticks perfectly. The Storage floor is COMPLETE!"


def setup(world, hour=None):
    rng = world.rng
    made = datetime(2026, rng.randint(1, 12), rng.randint(1, 28), hour if hour is not None else rng.randint(0, 23), rng.choice([0, 15, 30, 45]))
    inspected = made + timedelta(days=rng.randint(3, 400), hours=rng.randint(0, 23))
    return {"made_at": made.strftime("%Y-%m-%d %H:%M"), "inspected": inspected}


def check(ctx):
    for seed, hour in ((1, None), (2, 23), (3, 3), (4, 6), (5, 21), (6, 22)):
        r = ctx.run(seed=seed, setup_args={"hour": hour})
        ctx.need(r, "made", "warranty_ends", "ship_by", "label_date", "age_days", "night_shift")
        made = datetime.strptime(r.get("made_at"), "%Y-%m-%d %H:%M")
        ctx.expect(r.get("made") == made, "made should be made_at turned into a datetime with datetime.strptime(made_at, \"%Y-%m-%d %H:%M\").")
        ctx.expect(r.get("warranty_ends") == made + timedelta(days=1095), "warranty_ends should be made + timedelta(days=1095).")
        ctx.expect(r.get("ship_by") == made + timedelta(hours=48), "ship_by should be made + 48 hours.")
        ctx.expect(r.get("label_date") == made.strftime("%d/%m/%Y"),
                   f"label_date should look like {made.strftime('%d/%m/%Y')}: day/month/year. Try .strftime(\"%d/%m/%Y\").")
        ctx.expect(r.get("age_days") == (r.get("inspected") - made).days, "age_days should be (inspected - made).days.")
        night = made.hour >= 22 or made.hour < 6
        ctx.expect(r.get("night_shift") is night, f"A drive made at {made:%H:%M} should have night_shift = {night}.")
        if seed == 1:
            ctx.show("display", text=f"Made {made:%d/%m/%Y} · ship by {made + timedelta(hours=48):%d/%m}")
