from factory.web_sim import install_module, make_flask

SUCCESS = "🔌 The Factory API is live! Shops all over the country can now order ByteWorks computers automatically."


def setup(world):
    install_module("flask", make_flask())
    return {}


def check(ctx):
    r = ctx.run()
    ctx.need(r, "app", "orders")
    app, orders = r.get("app"), r.get("orders")
    orders.clear()  # start the checks from an empty shop
    c = app.test_client()

    def body(resp):
        data = resp.get_json()
        return resp.text if data is None else data

    ctx.expect(c.get("/orders").status_code == 200 and body(c.get("/orders")) == [],
               "GET /orders should return a JSON list of orders (an empty list to start with): jsonify(list(orders.values())).")
    made = []
    for model in ["Gaming PC", "Office PC", "Mini PC"]:
        resp = c.post("/orders", json={"model": model})
        ctx.expect(resp.status_code == 201, f"POST /orders should return status 201 (Created), but gave {resp.status_code}.")
        made.append(body(resp))
    ctx.expect(made == [{"id": i, "model": m, "status": "pending"} for i, m in enumerate(["Gaming PC", "Office PC", "Mini PC"], 1)],
               f"POST /orders should return the new order like {{'id': 1, 'model': 'Gaming PC', 'status': 'pending'}}. Got {made[0]!r}.")
    ctx.expect(body(c.get("/orders")) == made, "GET /orders should list every order you created.")

    one = c.get("/orders/2")
    ctx.expect(one.status_code == 200 and body(one) == made[1], "GET /orders/2 should return order 2.")
    missing = c.get("/orders/99")
    ctx.expect(missing.status_code == 404, "GET /orders/99 should return status 404: that order doesn't exist.")
    ctx.expect(body(missing) == {"error": "not found"}, 'A missing order should return jsonify({"error": "not found"}).')

    upd = c.put("/orders/1", json={"status": "shipped"})
    ctx.expect(upd.status_code == 200 and body(upd) == {"id": 1, "model": "Gaming PC", "status": "shipped"},
               "PUT /orders/1 with {\"status\": \"shipped\"} should update the status and return the order.")
    ctx.expect(body(c.get("/orders/1"))["status"] == "shipped", "The PUT should actually change the stored order.")
    ctx.expect(c.put("/orders/99", json={"status": "shipped"}).status_code == 404, "PUT on a missing order should return 404.")

    gone = c.delete("/orders/3")
    ctx.expect(gone.status_code == 200 and body(gone) == {"deleted": 3}, "DELETE /orders/3 should return {\"deleted\": 3}.")
    ctx.expect(c.get("/orders/3").status_code == 404, "After DELETE, GET /orders/3 should be 404.")
    ctx.expect(c.delete("/orders/3").status_code == 404, "Deleting an order that's already gone should return 404.")
    again = c.post("/orders", json={"model": "Workstation"})
    ctx.expect(body(again).get("id") == 3, "After deleting order 3, the next new order's id should be one more than the biggest remaining id (2 + 1 = 3).")
    for o in made:
        ctx.show("part", label=f"order {o['id']}", result="reject" if o["id"] == 3 else "ship")
