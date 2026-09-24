from factory.web_sim import install_module, make_flask

SUCCESS = "🌐 The ByteWorks shop is ONLINE. Orders are already coming in!"


def setup(world):
    rng = world.rng
    install_module("flask", make_flask())
    parts = rng.sample(["ram", "cpu", "ssd", "gpu", "motherboard", "fan", "case"], 4)
    return {"stock": {p: rng.randint(0, 80) for p in parts}}


def check(ctx):
    for seed in range(1, 4):
        r = ctx.run(seed=seed)
        ctx.need(r, "app")
        app, stock = r.get("app"), r.get("stock")
        ctx.expect(hasattr(app, "test_client"), "app should be Flask(__name__).")
        c = app.test_client()
        home = c.get("/")
        ctx.expect(home.status_code == 200, "There's no page at / yet. Add @app.route(\"/\") above a home() function.")
        ctx.expect(home.text == "<h1>ByteWorks Shop</h1>", f"/ should return <h1>ByteWorks Shop</h1> but returned {home.text!r}.")
        about = c.get("/about")
        ctx.expect(about.status_code == 200, "There's no /about page yet.")
        ctx.expect(about.text == "Hand-built computers since Day 1", "/about should return: Hand-built computers since Day 1")
        for part, qty in stock.items():
            page = c.get(f"/stock/{part}")
            ctx.expect(page.status_code == 200, f"/stock/{part} should work. Use @app.route(\"/stock/<part>\").")
            ctx.expect(page.text == f"{part}: {qty} in stock", f"/stock/{part} should say {part}: {qty} in stock")
        missing = c.get("/stock/unicorn")
        ctx.expect(missing.text == "We don't sell unicorn", "/stock/unicorn should say We don't sell unicorn")
        ctx.expect(missing.status_code == 404, "A part we don't sell should return status 404: return \"...\", 404")
        if seed == 1:
            for part, qty in stock.items():
                ctx.show("part", label=f"/stock/{part}"[:11], result="ship")
            ctx.show("part", label="/unicorn", result="reject")
