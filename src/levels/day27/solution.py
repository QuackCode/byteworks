# Day 27: You're given new_order, more_orders, ship_id and cancel_id
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client["byteworks"]
orders = db["orders"]

# 2. insert the new orders
orders.insert_one(new_order)
orders.insert_many(more_orders)

pending = list(orders.find({"status": "pending"}))
big_spenders = list(orders.find({"price": {"$gte": 1000}}))

# 5. ship one order
orders.update_one({"order_id": ship_id}, {"$set": {"status": "shipped"}})

# 6. cancel one order
orders.delete_one({"order_id": cancel_id})

pending_count = orders.count_documents({"status": "pending"})
print(len(pending), "pending before, now", pending_count)
