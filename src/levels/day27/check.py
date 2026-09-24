import copy

from factory.mongo_sim import Server, make_pymongo, matches
from factory.web_sim import install_module

SUCCESS = "🗃️ Orders safely stored. Restart the server all you like, nothing gets lost!"

MODELS = [("Gaming PC", 1499), ("Office PC", 649), ("Workstation", 2199), ("Mini PC", 449), ("Streaming PC", 1099)]


def make_order(rng, oid, status=None):
    model, price = rng.choice(MODELS)
    return {"order_id": oid, "model": model, "price": price, "status": status or rng.choice(["pending", "pending", "shipped"])}


def setup(world):
    rng = world.rng
    server = Server()
    existing = [make_order(rng, i) for i in range(1, rng.randint(6, 9))]
    col = server.db("byteworks")["orders"]
    for o in existing:
        col.insert_one(o)
    n = len(existing)
    new_order = make_order(rng, n + 1, "pending")
    more = [make_order(rng, n + 2 + i, "pending") for i in range(rng.randint(2, 4))]
    pend = [o["order_id"] for o in existing + [new_order] + more if o["status"] == "pending"]
    ship_id, cancel_id = rng.sample(pend, 2)
    install_module("pymongo", make_pymongo(server))
    return {"_server": server, "_start": copy.deepcopy(existing), "new_order": new_order, "more_orders": more,
            "ship_id": ship_id, "cancel_id": cancel_id}


def check(ctx):
    for seed in range(1, 4):
        r = ctx.run(seed=seed)
        ctx.need(r, "client", "db", "orders", "pending", "big_spenders", "pending_count")
        col = r.get("_server").db("byteworks")["orders"]
        everything = r.get("_start") + [r.get("new_order")] + r.get("more_orders")
        strip = lambda docs: [{k: v for k, v in d.items() if k != "_id"} for d in docs]
        ctx.expect(r.get("orders") is col,
                   'orders should be the "orders" collection in the "byteworks" database: client["byteworks"]["orders"].')
        new_id = r.get("new_order")["order_id"]
        ctx.expect(new_id == r.get("cancel_id") or any(d["order_id"] == new_id for d in col.docs),
                   "Insert new_order with orders.insert_one(new_order).")
        ctx.expect(strip(r.get("pending")) == [d for d in everything if d["status"] == "pending"],
                   'pending should be list(orders.find({"status": "pending"})), found AFTER inserting the new orders.')
        ctx.expect(strip(r.get("big_spenders")) == [d for d in everything if d["price"] >= 1000],
                   'big_spenders should be the orders with price 1000 or more: {"price": {"$gte": 1000}}.')
        final = {d["order_id"]: d for d in copy.deepcopy(everything)}
        final[r.get("ship_id")]["status"] = "shipped"
        del final[r.get("cancel_id")]
        ids = [d["order_id"] for d in col.docs]
        ctx.expect(r.get("cancel_id") not in ids, "The cancelled order is still there. Use orders.delete_one({\"order_id\": cancel_id}).")
        ctx.expect(sorted(ids) == sorted(final), "The orders in the database aren't right. Did you insert new_order AND every order in more_orders?")
        shipped = next(d for d in col.docs if d["order_id"] == r.get("ship_id"))
        ctx.expect(shipped["status"] == "shipped", 'Mark ship_id as shipped: update_one({"order_id": ship_id}, {"$set": {"status": "shipped"}}).')
        ctx.expect(strip(col.docs) == list(final.values()), "Only the ship_id order should change, and only its status.")
        ctx.expect(r.get("pending_count") == sum(d["status"] == "pending" for d in final.values()),
                   "pending_count should be counted AFTER shipping and cancelling: orders.count_documents({\"status\": \"pending\"}).")
        if seed == 1:
            for d in everything[:10]:
                oid = d["order_id"]
                ctx.show("part", label=f"order {oid}", result="reject" if oid == r.get("cancel_id") else "ship")
