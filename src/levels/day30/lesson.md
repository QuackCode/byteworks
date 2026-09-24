## The final shift 🏁

Thirty days ago you printed `Factory online`. Today you'll build real computers from start to finish. Here's everything you'll use:

| Skill | From | Where it shows up today |
|---|---|---|
| Variables, strings, f-strings | Days 2–4 | serials, messages |
| Lists, tuples, dicts | Days 5–8 | parts, specs, orders, computers |
| Conditionals | Day 9 | gaming vs office rules |
| Loops, break/return | Day 10 | keep fetching until a good part turns up |
| Functions & lambdas | Days 11, 13 | `fetch_good`, part tests |
| Modules | Day 12 | `grade` from `factory.cpu_tools` |
| Higher-order functions | Day 14 | passing a test function into `fetch_good` |
| Exception handling | Day 17 | exploding motherboards |
| Files & JSON | Day 19 | `shipped.json` |

## Passing functions as tests

The clever bit is `fetch_good(kind, is_good)`. It doesn't care **what** makes a part good. You pass that in as a function:

```python
def first_match(items, is_good):
    for item in items:
        if is_good(item):
            return item

print(first_match([3, 8, 12, 5], lambda n: n > 10))
print(first_match(["ram", "cpu", "gpu"], lambda s: s.startswith("c")))
```

## Lambdas can use variables from around them

```python
for order in [{"type": "GAMING"}, {"type": "OFFICE"}]:
    min_score = 8000 if order["type"] == "GAMING" else 5000
    good_gpu = lambda g: g["score"] >= min_score
    print(order["type"], good_gpu({"score": 6500}))
```

## The quality rules

| Part | Good if… |
|---|---|
| **CPU** | `grade(cpu)` is `"GAMING"` for **GAMING** orders. **OFFICE** orders accept anything except `"REJECT"` |
| **RAM** | its `spec` is exactly `(32, 5600)` |
| **SSD** | its `health` is 20 or more |
| **Motherboard** | `tester.install(board)` works. It **raises** `ValueError` or `KeyError` for faulty boards |
| **GPU** | its `score` is at least **8000** for GAMING orders, or **5000** for OFFICE orders |

Every faulty part you fetch must be sent back with `warehouse.scrap(part)`.

## Your task

You're given `orders` (a list like `{"id": 1, "type": "GAMING"}`), `warehouse` (`warehouse.fetch(kind)` and `warehouse.scrap(part)`) and `tester`.

1. Finish `fetch_good(kind, is_good)`: keep fetching parts of that kind, scrapping bad ones, until you get one where `is_good(part)` is `True`, then return it
2. Finish `board_ok(board)`: return `True` if `tester.install(board)` works, or `False` if it raises `ValueError` or `KeyError`
3. For every order, build a computer dict: `{"order": id, "cpu": serial, "ram": serial, "ssd": serial, "motherboard": serial, "gpu": serial}` and add it to `computers`
4. Save `computers` to `shipped.json` with `json.dump`

Run it as many times as you like. The faults are different in every test, so your rules have to be right! 💪
