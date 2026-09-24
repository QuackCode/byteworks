## What is web scraping?

Web pages are made of **HTML**: text wrapped in **tags** like `<h1>`, `<p>` and `<table>`. **Scraping** means downloading a page with code and pulling out the bits of data you need.

```
<h1>GPU Chips</h1>
<table>
  <tr class="chip">
    <td class="name">GX-4070</td>
    <td class="price">£412.50</td>
  </tr>
</table>
```

- `<tr>` is a table **row** and `<td>` is a **cell**
- `class="..."` labels an element, which is very handy for finding it

## Step 1: download the page with `requests`

`requests` is the most popular Python package for talking to websites:

```python
import requests
resp = requests.get("https://chipco.example/gpus")
print(resp.status_code)      # 200 means OK
print(resp.text[:120])       # the HTML, as one big string
```

(In ByteWorks, ChipCo's website is a pretend one, so your code never touches the real internet.)

## Step 2: parse it with BeautifulSoup

**BeautifulSoup** (from the `bs4` package) turns HTML text into a searchable object:

```python
from bs4 import BeautifulSoup
html = "<h1>Hello</h1><p class='note'>First</p><p class='note'>Second</p>"
soup = BeautifulSoup(html, "html.parser")
print(soup.find("h1").text)                     # the first <h1>
notes = soup.find_all("p", class_="note")       # EVERY matching <p>
print([p.text for p in notes])
```

| Method | Gives you |
|---|---|
| `soup.find("tag")` | the first matching element |
| `soup.find_all("tag")` | a list of all matches |
| `find(..., class_="x")` | match by class (note the `_`!) |
| `element.text` | the text inside |
| `element["href"]` | an attribute's value |

You can search **inside** an element too, e.g. `row.find("td", class_="price")`.

## Scrape responsibly 🤝

Real websites belong to real people:
- Check the site's **terms** and its `robots.txt` file (e.g. `example.com/robots.txt`) to see what's allowed
- Don't hammer a site with thousands of requests. Go slowly
- If the site offers an **API**, use that instead (Day 28!)
- Never scrape personal data

## Your task

1. Download `https://chipco.example/gpus` into `resp`
2. Make `soup` from `resp.text` using `"html.parser"`
3. `heading`: the text of the page's `<h1>`
4. `rows`: every `<tr>` with class `chip`
5. `prices`: a dict of chip **name → price as a float** (e.g. `"£412.50"` → `412.5`)
6. `in_stock`: names of the chips whose stock cell says exactly `In stock`
7. `cheapest`: the in-stock chip with the lowest price
