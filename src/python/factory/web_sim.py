"""Pretend versions of `requests` and `flask`.

A browser can't run a real web server, and ByteWorks shouldn't hit real websites, so these
behave like the real libraries for the parts the lessons use. Levels register them under
their real names (sys.modules["requests"]), so players write the same imports as in real life.
"""
import json as _json
import re
import sys
import types
from urllib.parse import parse_qs, urlencode, urlparse

from .core import FactoryError


# ---------------------------------------------------------------- requests

class Response:
    def __init__(self, status_code=200, text="", data=None, headers=None):
        self.status_code = status_code
        self._data = data
        self.text = text if data is None else _json.dumps(data)
        self.headers = headers or {"Content-Type": "application/json" if data is not None else "text/html"}

    @property
    def ok(self):
        return self.status_code < 400

    def json(self):
        if self._data is None:
            try:
                return _json.loads(self.text)
            except ValueError:
                raise ValueError("This response isn't JSON. Try .text instead.") from None
        return _json.loads(_json.dumps(self._data))  # a fresh copy each time, like real JSON

    def __repr__(self):
        return f"<Response [{self.status_code}]>"


def make_requests(handler):
    """handler(method, url, params, json_body) -> Response. Returns a module that looks like `requests`."""
    mod = types.ModuleType("requests")
    mod.calls = []

    def _call(method, url, params=None, json=None):
        if not isinstance(url, str) or not url.startswith(("http://", "https://")):
            raise FactoryError(f"{url!r} isn't a web address. It should start with https://")
        parsed = urlparse(url)
        query = {k: v[0] for k, v in parse_qs(parsed.query).items()}
        query.update({k: str(v) for k, v in (params or {}).items()})
        base = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        mod.calls.append((method, base, dict(query), json))
        return handler(method, base, query, json)

    mod.get = lambda url, params=None, **kw: _call("GET", url, params)
    mod.post = lambda url, json=None, params=None, **kw: _call("POST", url, params, json)
    mod.put = lambda url, json=None, params=None, **kw: _call("PUT", url, params, json)
    mod.delete = lambda url, params=None, **kw: _call("DELETE", url, params)
    mod.Response = Response
    return mod


def install_module(name, module):
    sys.modules[name] = module
    return module


# ---------------------------------------------------------------- flask

class TestResponse(Response):
    """Like Flask's test client response: .get_json() / .json, plus .text and .status_code."""

    @property
    def json(self):
        return self.get_json()

    def get_json(self):
        return Response.json(self) if self._data is not None else None

class _Request:
    """The `request` object: filled in while a route function is running."""

    def __init__(self):
        self.method = None
        self.path = None
        self.args = {}
        self.json = None


request = _Request()


class _JsonBody:
    def __init__(self, data):
        self.data = data


def jsonify(*args, **kwargs):
    return _JsonBody(args[0] if len(args) == 1 else list(args) if args else kwargs)


def _to_regex(rule):
    def conv(m):
        kind, name = (m.group(1) or "string"), m.group(2)
        return f"(?P<{name}>\\d+)" if kind == "int" else f"(?P<{name}>[^/]+)"
    pattern = re.sub(r"<(?:(int|string):)?(\w+)>", conv, rule)
    return re.compile(f"^{pattern}$")


class Flask:
    def __init__(self, import_name=None):
        self.routes = []

    def route(self, rule, methods=None):
        methods = [m.upper() for m in (methods or ["GET"])]

        def decorator(func):
            self.routes.append((rule, _to_regex(rule), methods, func))
            return func
        return decorator

    def get(self, rule):
        return self.route(rule, ["GET"])

    def post(self, rule):
        return self.route(rule, ["POST"])

    def run(self, *args, **kwargs):
        print(" * ByteWorks web server ready (in real Flask this starts http://127.0.0.1:5000)")

    def test_client(self):
        return _Client(self)

    def dispatch(self, method, path, json_body=None):
        parsed = urlparse(path)
        allowed = False
        for rule, regex, methods, func in self.routes:
            m = regex.match(parsed.path)
            if not m:
                continue
            allowed = True
            if method not in methods:
                continue
            kwargs = {k: int(v) if v.isdigit() and f"<int:{k}>" in rule else v for k, v in m.groupdict().items()}
            request.method, request.path = method, parsed.path
            request.args = {k: v[0] for k, v in parse_qs(parsed.query).items()}
            request.json = json_body
            try:
                return _make_response(func(**kwargs))
            finally:
                request.json = None
        if allowed:
            return TestResponse(405, "405 Method Not Allowed")
        return TestResponse(404, "404 Not Found")


def _make_response(rv):
    status = 200
    if isinstance(rv, tuple):
        rv, status = rv[0], rv[1]
    if isinstance(rv, _JsonBody):
        return TestResponse(status, data=rv.data)
    if isinstance(rv, (dict, list)):
        return TestResponse(status, data=rv)
    if rv is None:
        raise FactoryError("A route function returned None. Every route must return something (text, a dict, or jsonify(...)).")
    return TestResponse(status, str(rv))


class _Client:
    def __init__(self, app):
        self.app = app

    def get(self, path):
        return self.app.dispatch("GET", path)

    def post(self, path, json=None):
        return self.app.dispatch("POST", path, json)

    def put(self, path, json=None):
        return self.app.dispatch("PUT", path, json)

    def delete(self, path):
        return self.app.dispatch("DELETE", path)


def make_flask():
    mod = types.ModuleType("flask")
    mod.Flask = Flask
    mod.request = request
    mod.jsonify = jsonify
    mod.render_template_string = lambda source, **ctx: re.sub(
        r"\{\{\s*(\w+)\s*\}\}", lambda m: str(ctx.get(m.group(1), "")), source)
    return mod
