## Why a database?

Variables disappear when a program stops. Files work, but finding "all pending orders over £1000" in a big text file is slow and fiddly. A **database** stores data safely and lets you search it quickly, even with millions of records and many users at once.

There are two big families:
- **SQL databases** (MySQL, PostgreSQL, SQLite) store data in tables with fixed columns
- **NoSQL / document databases** like **MongoDB** store **documents**, which look exactly like Python dicts

## MongoDB's structure

```
server
 └── database        "byteworks"
      └── collection  "orders"       (like a table)
           └── documents             {"order_id": 1, "model": "Gaming PC", "status": "pending"}
```

## Connecting with pymongo

```python
from pymongo import MongoClient
client = MongoClient("mongodb://localhost:27017")
db = client["byteworks"]
tests = db["test_orders"]
tests.insert_one({"model": "Mini PC", "price": 450})
print(list(tests.find()))
```

Every document automatically gets a unique `_id`.

(In ByteWorks the database is a pretend one that lives inside your browser tab.)

## CRUD: Create, Read, Update, Delete

```python
from pymongo import MongoClient
db = MongoClient("mongodb://localhost:27017")["demo"]
parts = db["parts"]

# Create
parts.insert_one({"name": "fan", "qty": 5})
parts.insert_many([{"name": "case", "qty": 2}, {"name": "psu", "qty": 0}])

# Read
print(parts.find_one({"name": "fan"}))
print(list(parts.find({"qty": 0})))           # all matching
print(parts.count_documents({}))              # {} matches everything

# Update ($set changes fields, $inc adds to a number)
parts.update_one({"name": "psu"}, {"$set": {"qty": 10}})
parts.update_one({"name": "fan"}, {"$inc": {"qty": 1}})

# Delete
parts.delete_one({"name": "case"})
print(list(parts.find()))
```

## Query operators

| Operator | Means | Example |
|---|---|---|
| `$gt` / `$gte` | greater than / or equal | `{"price": {"$gt": 500}}` |
| `$lt` / `$lte` | less than / or equal | `{"qty": {"$lt": 3}}` |
| `$ne` | not equal | `{"status": {"$ne": "shipped"}}` |
| `$in` | one of a list | `{"model": {"$in": ["Mini PC", "Office PC"]}}` |

## Your task

The `byteworks` database already has an `orders` collection. You're given `new_order` (a dict), `more_orders` (a list of dicts), `ship_id` and `cancel_id`.

1. Connect: `client`, then `db = client["byteworks"]` and `orders = db["orders"]`
2. Insert `new_order`, then insert all of `more_orders`
3. `pending`: a **list** of all orders whose `status` is `"pending"`
4. `big_spenders`: a list of orders with a `price` of **1000 or more**
5. Mark the order with `order_id` equal to `ship_id` as `"shipped"`
6. Delete the order with `order_id` equal to `cancel_id`
7. `pending_count`: how many orders are **still** pending (count **after** steps 5 and 6)
