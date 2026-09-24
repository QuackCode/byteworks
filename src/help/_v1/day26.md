## How websites work (the short version)

1. Your browser asks a **server** for an address like `/about`: a **request**
2. The server runs some code and sends back a **response**: usually HTML, plus a **status code**
   - `200` OK · `404` Not Found · `500` server error · `201` Created

**Flask** is a small, popular Python package for writing that server code.

## A tiny Flask app

```python
from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "<h1>Hello from ByteWorks!</h1>"

client = app.test_client()      # a pretend browser, for testing
page = client.get("/")
print(page.status_code, page.text)
```

- `app = Flask(__name__)` creates the web app
- `@app.route("/")` is a **decorator** (remember Day 14?) that connects the address `/` to the `home` function
- Whatever the function **returns** becomes the page

On a real computer, you'd add `app.run(debug=True)` and visit `http://127.0.0.1:5000` in your browser. In ByteWorks we use `app.test_client()` to visit pages from code.

## Several pages

```python
from flask import Flask
app = Flask(__name__)

@app.route("/")
def home():
    return "Home"

@app.route("/contact")
def contact():
    return "Email us!"

client = app.test_client()
print(client.get("/contact").text)
print(client.get("/nope").status_code)    # 404: no route for that address
```

## Variables in the address

Put `<name>` in the route, and Flask passes that part of the address into your function:

```python
from flask import Flask
app = Flask(__name__)

@app.route("/parts/<name>")
def part(name):
    return f"You asked about {name}"

print(app.test_client().get("/parts/ram").text)
```

`<int:order_id>` turns that part into an integer.

## Choosing the status code

Return a **tuple** of `(body, status)`:

```python
from flask import Flask
app = Flask(__name__)

@app.route("/secret")
def secret():
    return "Staff only!", 403

print(app.test_client().get("/secret").status_code)
```

## Templates

Real sites keep HTML in **template** files (Flask uses a template language called Jinja) and fill in the gaps with `{{ variable }}`: `render_template("page.html", name=name)`. For short snippets there's `render_template_string`:

```python
from flask import Flask, render_template_string
print(render_template_string("<p>Hi {{ name }}!</p>", name="Ada"))
```

## Your task

You're given `stock`, a dict like `{"ram": 40, "cpu": 12}`. Build `app` with three routes:

1. `/` returns `<h1>ByteWorks Shop</h1>`
2. `/about` returns `Hand-built computers since Day 1`
3. `/stock/<part>` returns `<part>: <number> in stock` (e.g. `ram: 40 in stock`). If the part isn't in `stock`, it returns `We don't sell <part>` with status **404**
