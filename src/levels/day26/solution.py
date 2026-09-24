# Day 26: You're given stock, a dict of part -> how many we have
from flask import Flask

app = Flask(__name__)


@app.route("/")
def home():
    return "<h1>ByteWorks Shop</h1>"


@app.route("/about")
def about():
    return "Hand-built computers since Day 1"


@app.route("/stock/<part>")
def stock_page(part):
    if part in stock:
        return f"{part}: {stock[part]} in stock"
    return f"We don't sell {part}", 404


client = app.test_client()
print(client.get("/").text)
