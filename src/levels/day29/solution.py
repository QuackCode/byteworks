# Day 29: Build the ByteWorks order API
from flask import Flask, jsonify, request

app = Flask(__name__)
orders = {}   # id -> order dict


@app.route("/orders", methods=["GET"])
def list_orders():
    return jsonify(list(orders.values()))


@app.route("/orders", methods=["POST"])
def create_order():
    new_id = max(orders, default=0) + 1
    order = {"id": new_id, "model": request.json["model"], "status": "pending"}
    orders[new_id] = order
    return jsonify(order), 201


@app.route("/orders/<int:order_id>", methods=["GET"])
def get_order(order_id):
    if order_id not in orders:
        return jsonify({"error": "not found"}), 404
    return jsonify(orders[order_id])


@app.route("/orders/<int:order_id>", methods=["PUT"])
def update_order(order_id):
    if order_id not in orders:
        return jsonify({"error": "not found"}), 404
    orders[order_id]["status"] = request.json["status"]
    return jsonify(orders[order_id])


@app.route("/orders/<int:order_id>", methods=["DELETE"])
def delete_order(order_id):
    if order_id not in orders:
        return jsonify({"error": "not found"}), 404
    del orders[order_id]
    return jsonify({"deleted": order_id})


c = app.test_client()
print(c.post("/orders", json={"model": "Gaming PC"}).get_json())
print(c.get("/orders").get_json())
