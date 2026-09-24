from factory.web_sim import Response, install_module, make_requests

SUCCESS = "🕸️ Prices scraped in milliseconds. Nobody has to copy them by hand ever again!"

URL = "https://chipco.example/gpus"


def build_catalogue(rng):
    names = rng.sample(["GX-4060", "GX-4070", "GX-4080", "GX-4090", "RD-7600", "RD-7800", "RD-7900", "AR-B580", "AR-B770"], rng.randint(5, 7))
    chips = []
    for n in names:
        chips.append((n, round(rng.uniform(180, 1400), 2), "In stock" if rng.random() < 0.7 else "Out of stock"))
    if all(s != "In stock" for _, _, s in chips):
        chips[0] = (chips[0][0], chips[0][1], "In stock")
    # the cheapest chip overall is sold out, to catch anyone who forgets the stock check
    cheapest = min(range(len(chips)), key=lambda i: chips[i][1])
    chips[cheapest] = (chips[cheapest][0], chips[cheapest][1], "Out of stock")
    if all(s != "In stock" for _, _, s in chips):
        other = (cheapest + 1) % len(chips)
        chips[other] = (chips[other][0], chips[other][1], "In stock")
    return chips


def html_for(chips, heading):
    rows = "\n".join(
        f'    <tr class="chip"><td class="name">{n}</td><td class="price">£{p:.2f}</td><td class="stock">{s}</td></tr>'
        for n, p, s in chips)
    return f"""<html>
<head><title>ChipCo | Catalogue</title></head>
<body>
  <nav><a href="/">Home</a> | <a href="/about">About</a></nav>
  <h1>{heading}</h1>
  <p class="note">Prices include VAT. Updated daily.</p>
  <table id="catalogue">
    <tr><th>Chip</th><th>Price</th><th>Stock</th></tr>
{rows}
  </table>
  <a class="next" href="/gpus?page=2">Next page</a>
</body>
</html>"""


def setup(world):
    rng = world.rng
    chips = build_catalogue(rng)
    heading = rng.choice(["GPU Chips", "Graphics Processors", "GPU Chip Catalogue"])
    page = html_for(chips, heading)

    def handler(method, url, params, body):
        if method == "GET" and url == URL:
            return Response(200, page)
        return Response(404, "<h1>404 Not Found</h1>")

    install_module("requests", make_requests(handler))
    return {"_chips": chips, "_heading": heading}


def check(ctx):
    for seed in range(1, 4):
        r = ctx.run(seed=seed)
        ctx.need(r, "resp", "soup", "heading", "rows", "prices", "in_stock", "cheapest")
        chips, heading = r.get("_chips"), r.get("_heading")
        ctx.expect(getattr(r.get("resp"), "status_code", None) == 200, f"resp should be requests.get(\"{URL}\"). Check the address.")
        ctx.expect(type(r.get("soup")).__name__ == "BeautifulSoup", "soup should be BeautifulSoup(resp.text, \"html.parser\").")
        ctx.expect(str(r.get("heading")).strip() == heading, f"heading should be the <h1> text: {heading!r}.")
        ctx.expect(len(r.get("rows")) == len(chips), f"rows should be the {len(chips)} <tr> rows with class chip (use class_=\"chip\").")
        prices = {n: p for n, p, _ in chips}
        ctx.expect(r.get("prices") == prices, "prices should map each chip name to its price as a float, without the £ sign.")
        in_stock = [n for n, _, s in chips if s == "In stock"]
        ctx.expect(r.get("in_stock") == in_stock, "in_stock should list the names of chips whose stock cell says In stock.")
        cheapest = min(in_stock, key=lambda n: prices[n])
        ctx.expect(r.get("cheapest") == cheapest,
                   f"cheapest should be {cheapest}: the lowest price among IN-STOCK chips (the cheapest overall is sold out!).")
        if seed == 1:
            for n, p, s in chips:
                ctx.show("part", label=n, result="ship" if s == "In stock" else "reject")
