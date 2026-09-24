# Day 27: You're given new_order, more_orders, ship_id and cancel_id
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = ____
orders = ____

# 2. insert the new orders

pending = ____
big_spenders = ____

# 5. ship one order

# 6. cancel one order

pending_count = ____
print(len(pending), "pending before, now", pending_count)
