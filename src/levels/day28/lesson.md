## What's an API?

A website is built for **people**, so it's full of pictures, buttons and layout. An **API** (Application Programming Interface) is built for **programs**: you send a request to a web address and get back pure data, usually as **JSON**.

Scraping (Day 22) is like reading prices off a shop window. An API is like the shop handing you its price list. When there's an API, use it!

## HTTP methods

| Method | Used to… | Example |
|---|---|---|
| `GET` | **read** data | get delivery quotes |
| `POST` | **create** something | book a delivery |
| `PUT` | **update** something | change the address |
| `DELETE` | **remove** something | cancel a booking |

## Status codes

| Code | Meaning |
|---|---|
| `200` | OK |
| `201` | Created (usually after a POST) |
| `400` | Bad request: you sent something wrong |
| `401` / `403` | Not logged in / not allowed |
| `404` | Not found |
| `500` | The server broke |

## Calling an API with `requests`

```python
import requests
resp = requests.get("https://api.swiftship.example/rates", params={"weight_kg": 3})
print(resp.status_code)
quotes = resp.json()          # JSON text → Python lists and dicts
print(quotes[0])
```

`params=` adds the `?weight_kg=3` part to the address for you.

## Sending data

```python
import requests
resp = requests.post("https://api.swiftship.example/bookings",
                     json={"service": "SwiftShip Economy", "weight_kg": 3})
print(resp.status_code, resp.json())
```

## Always check the status!

```python
import requests
resp = requests.get("https://api.swiftship.example/track/NOPE-000")
if resp.status_code == 200:
    print(resp.json()["status"])
else:
    print("Problem:", resp.status_code)
```

Real APIs often need an **API key** (a password for programs) sent with each request. Keep keys secret: never put them in code you share!

(In ByteWorks, SwiftShip is a pretend courier that lives in your browser.)

## Your task

The addresses are given to you as `RATES_URL`, `BOOK_URL` and `TRACK_URL`, along with `weight_kg` and `lost_parcel`.

1. `resp`: **GET** `RATES_URL` with the parameter `weight_kg`
2. `quotes`: the JSON from `resp`: a list of dicts with `service`, `price` and `days`
3. `fast`: only the quotes that arrive in **2 days or fewer**
4. `best`: the **cheapest** of the fast quotes
5. `booking`: **POST** to `BOOK_URL` with the JSON `{"service": <best's service>, "weight_kg": weight_kg}`
6. `tracking`: the `"tracking"` value from the booking's JSON
7. `lost`: **GET** `TRACK_URL + lost_parcel`. `parcel_status` is its JSON `"status"` if the status code is 200, otherwise the text `"not found"`
