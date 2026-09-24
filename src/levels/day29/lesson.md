## Building your own API

Yesterday you **used** an API. Today you'll **build** one. Other programs will send requests to your Flask app and get JSON back.

A **REST API** organises things around **resources** (like orders) and uses HTTP methods for the four **CRUD** actions:

| Action | Method | Address | Returns |
|---|---|---|---|
| **R**ead all | `GET` | `/orders` | a list of orders |
| **C**reate | `POST` | `/orders` | the new order, status `201` |
| **R**ead one | `GET` | `/orders/3` | order 3, or `404` |
| **U**pdate | `PUT` | `/orders/3` | the updated order |
| **D**elete | `DELETE` | `/orders/3` | confirmation |

## Choosing methods in Flask

```python
from flask import Flask, jsonify, request

app = Flask(__name__)
notes = []

@app.route("/notes", methods=["GET"])
def all_notes():
    return jsonify(notes)

@app.route("/notes", methods=["POST"])
def add_note():
    data = request.json            # the JSON the caller sent
    notes.append(data["text"])
    return jsonify({"added": data["text"]}), 201

c = app.test_client()
print(c.post("/notes", json={"text": "Buy fans"}).status_code)
print(c.get("/notes").get_json())
```

- `methods=[...]` chooses which HTTP methods a route answers
- `request.json` is the data sent with a POST or PUT
- `jsonify(...)` sends Python data back as JSON

## Numbers in the address

```python
from flask import Flask, jsonify
app = Flask(__name__)
items = {1: "fan", 2: "case"}

@app.route("/items/<int:item_id>", methods=["GET"])
def one_item(item_id):
    if item_id not in items:
        return jsonify({"error": "not found"}), 404
    return jsonify({"id": item_id, "name": items[item_id]})

c = app.test_client()
print(c.get("/items/2").get_json(), c.get("/items/9").status_code)
```

## Your task

`orders` starts as an empty dict (`id → order`). Build these routes on `app`:

1. **`GET /orders`** returns a list of every order
2. **`POST /orders`** takes JSON like `{"model": "Gaming PC"}` and creates `{"id": <new id>, "model": ..., "status": "pending"}`. The new id is one more than the biggest id so far (the first order gets 1). Store it and return it with status **201**
3. **`GET /orders/<int:order_id>`** returns that order, or `{"error": "not found"}` with **404**
4. **`PUT /orders/<int:order_id>`** takes JSON like `{"status": "shipped"}`, updates the order's status and returns the order (**404** if missing)
5. **`DELETE /orders/<int:order_id>`** removes it and returns `{"deleted": <id>}` (**404** if missing)
