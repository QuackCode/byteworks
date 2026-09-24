from factory.web_sim import Response, install_module, make_requests

SUCCESS = "🚚 Booked, tracked and on its way. SwiftShip says you're their favourite customer!"

BASE = "https://api.swiftship.example"
SERVICES = [("SwiftShip Economy", 1.2, 5), ("SwiftShip Standard", 1.9, 3), ("SwiftShip Express", 3.1, 2),
            ("SwiftShip NextDay", 4.4, 1), ("SwiftShip Rocket", 7.5, 1), ("SwiftShip Saver", 0.9, 7)]


def setup(world):
    rng = world.rng
    services = [(n, round(rate * rng.uniform(0.7, 1.4), 2), d) for n, rate, d in SERVICES]
    parcels = {f"SS-{rng.randint(1000, 9999)}": rng.choice(["in transit", "at depot", "out for delivery"]) for _ in range(3)}
    known = rng.random() < 0.5
    lost = rng.choice(list(parcels)) if known else f"SS-{rng.randint(10000, 99999)}"
    state = {"bookings": []}

    def handler(method, url, params, body):
        if url == f"{BASE}/rates" and method == "GET":
            if "weight_kg" not in params:
                return Response(400, data={"error": "weight_kg is required"})
            w = float(params["weight_kg"])
            return Response(200, data=[{"service": n, "price": round(4 + rate * w, 2), "days": d} for n, rate, d in services])
        if url == f"{BASE}/bookings" and method == "POST":
            if not isinstance(body, dict) or "service" not in body or "weight_kg" not in body:
                return Response(400, data={"error": "Send JSON with service and weight_kg"})
            tracking = f"SS-{rng.randint(10000, 99999)}"
            state["bookings"].append(dict(body, tracking=tracking))
            return Response(201, data={"tracking": tracking, "service": body["service"]})
        if url.startswith(f"{BASE}/track/") and method == "GET":
            pid = url.rsplit("/", 1)[-1]
            if pid in parcels:
                return Response(200, data={"parcel": pid, "status": parcels[pid]})
            return Response(404, data={"error": "No parcel with that ID"})
        return Response(404, data={"error": "Unknown endpoint"})

    install_module("requests", make_requests(handler))
    return {"RATES_URL": f"{BASE}/rates", "BOOK_URL": f"{BASE}/bookings", "TRACK_URL": f"{BASE}/track/",
            "weight_kg": rng.choice([1, 2.5, 4, 8, 15]), "lost_parcel": lost,
            "_parcels": parcels, "_state": state}


def check(ctx):
    for seed in range(1, 7):
        r = ctx.run(seed=seed)
        ctx.need(r, "resp", "quotes", "fast", "best", "booking", "tracking", "lost", "parcel_status")
        ctx.expect(r.get("resp").status_code == 200, "GET RATES_URL needs the weight: requests.get(RATES_URL, params={\"weight_kg\": weight_kg}).")
        quotes = r.get("resp").json()
        ctx.expect(r.get("quotes") == quotes, "quotes should be resp.json().")
        fast = [q for q in quotes if q["days"] <= 2]
        ctx.expect(r.get("fast") == fast, "fast should keep only quotes with days <= 2.")
        best = min(fast, key=lambda q: q["price"])
        ctx.expect(r.get("best") == best, f"best should be the cheapest FAST quote: {best['service']} at £{best['price']}.")
        bookings = r.get("_state")["bookings"]
        ctx.expect(len(bookings) == 1, "POST exactly one booking to BOOK_URL.")
        ctx.expect(bookings[0]["service"] == best["service"] and bookings[0]["weight_kg"] == r.get("weight_kg"),
                   "The booking JSON should be {\"service\": best[\"service\"], \"weight_kg\": weight_kg}.")
        ctx.expect(r.get("tracking") == bookings[0]["tracking"], "tracking should be booking.json()[\"tracking\"].")
        want = r.get("_parcels").get(r.get("lost_parcel"), "not found")
        ctx.expect(r.get("parcel_status") == want,
                   f"For parcel {r.get('lost_parcel')} parcel_status should be {want!r}. Check lost.status_code before using .json().")
        if seed == 1:
            for q in quotes:
                ctx.show("part", label=q["service"].split()[-1], result="ship" if q == best else "reject")
