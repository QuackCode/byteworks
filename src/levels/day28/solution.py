# Day 28: You're given RATES_URL, BOOK_URL, TRACK_URL, weight_kg and lost_parcel
import requests

resp = requests.get(RATES_URL, params={"weight_kg": weight_kg})
quotes = resp.json()
fast = [q for q in quotes if q["days"] <= 2]
best = min(fast, key=lambda q: q["price"])

booking = requests.post(BOOK_URL, json={"service": best["service"], "weight_kg": weight_kg})
tracking = booking.json()["tracking"]

lost = requests.get(TRACK_URL + lost_parcel)
parcel_status = lost.json()["status"] if lost.status_code == 200 else "not found"

print("Booked", best, "→ tracking", tracking)
print("Lost parcel:", parcel_status)
