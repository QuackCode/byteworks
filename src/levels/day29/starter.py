# Day 29: Build the ByteWorks order API
from flask import Flask, jsonify, request

app = Flask(__name__)
orders = {}   # id -> order dict


@app.route("/orders", methods=["GET"])
def list_orders():
    ____


@app.route("/orders", methods=["POST"])
def create_order():
    ____


# add GET, PUT and DELETE routes for /orders/<int:order_id>


c = app.test_client()
print(c.post("/orders", json={"model": "Gaming PC"}).get_json())
print(c.get("/orders").get_json())
