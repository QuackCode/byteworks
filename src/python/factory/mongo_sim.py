"""A pretend MongoDB (pymongo) that lives in memory. It supports the bits the lessons use."""
import copy
import types

from .core import FactoryError

OPS = {
    "$gt": lambda a, b: a is not None and a > b,
    "$gte": lambda a, b: a is not None and a >= b,
    "$lt": lambda a, b: a is not None and a < b,
    "$lte": lambda a, b: a is not None and a <= b,
    "$ne": lambda a, b: a != b,
    "$in": lambda a, b: a in b,
    "$nin": lambda a, b: a not in b,
}


def matches(doc, query):
    for key, want in (query or {}).items():
        have = doc.get(key)
        if isinstance(want, dict) and want and all(k.startswith("$") for k in want):
            for op, value in want.items():
                if op not in OPS:
                    raise FactoryError(f"The ByteWorks database doesn't understand {op}. Try {', '.join(OPS)}.")
                if not OPS[op](have, value):
                    return False
        elif have != want:
            return False
    return True


class InsertResult:
    def __init__(self, ids):
        self.inserted_ids = ids
        self.inserted_id = ids[0] if ids else None


class UpdateResult:
    def __init__(self, matched, modified):
        self.matched_count = matched
        self.modified_count = modified


class DeleteResult:
    def __init__(self, deleted):
        self.deleted_count = deleted


class Cursor(list):
    def sort(self, key, direction=1):
        return Cursor(sorted(self, key=lambda d: d.get(key), reverse=direction == -1))

    def limit(self, n):
        return Cursor(self[:n])


class Collection:
    def __init__(self, name):
        self.name = name
        self.docs = []
        self._next_id = 1

    def insert_one(self, doc):
        if not isinstance(doc, dict):
            raise FactoryError("insert_one needs a dict, like {\"model\": \"Gaming PC\"}.")
        doc = copy.deepcopy(doc)
        doc.setdefault("_id", self._next_id)
        self._next_id += 1
        self.docs.append(doc)
        return InsertResult([doc["_id"]])

    def insert_many(self, docs):
        return InsertResult([self.insert_one(d).inserted_id for d in docs])

    def find(self, query=None, projection=None):
        found = [copy.deepcopy(d) for d in self.docs if matches(d, query)]
        if projection:
            keep = {k for k, v in projection.items() if v}
            found = [{k: v for k, v in d.items() if k in keep or (k == "_id" and projection.get("_id", 1))} for d in found]
        return Cursor(found)

    def find_one(self, query=None):
        found = self.find(query)
        return found[0] if found else None

    def _update(self, query, update, many):
        if not update or not all(k in ("$set", "$inc") for k in update):
            raise FactoryError('Updates need an operator, e.g. {"$set": {"status": "shipped"}} or {"$inc": {"qty": 1}}.')
        matched = modified = 0
        for d in self.docs:
            if matches(d, query):
                matched += 1
                before = copy.deepcopy(d)
                d.update(update.get("$set", {}))
                for k, v in update.get("$inc", {}).items():
                    d[k] = d.get(k, 0) + v
                modified += d != before
                if not many:
                    break
        return UpdateResult(matched, modified)

    def update_one(self, query, update):
        return self._update(query, update, many=False)

    def update_many(self, query, update):
        return self._update(query, update, many=True)

    def delete_one(self, query):
        for i, d in enumerate(self.docs):
            if matches(d, query):
                del self.docs[i]
                return DeleteResult(1)
        return DeleteResult(0)

    def delete_many(self, query):
        before = len(self.docs)
        self.docs = [d for d in self.docs if not matches(d, query)]
        return DeleteResult(before - len(self.docs))

    def count_documents(self, query):
        return sum(matches(d, query) for d in self.docs)


class Database(dict):
    def __missing__(self, name):
        self[name] = Collection(name)
        return self[name]

    def __getattr__(self, name):
        return self[name]

    def list_collection_names(self):
        return list(self.keys())


class Server:
    def __init__(self):
        self.databases = {}

    def db(self, name):
        return self.databases.setdefault(name, Database())


def make_pymongo(server):
    mod = types.ModuleType("pymongo")

    class MongoClient:
        def __init__(self, url="mongodb://localhost:27017", *args, **kwargs):
            if not str(url).startswith(("mongodb://", "mongodb+srv://")):
                raise FactoryError("A MongoDB address starts with mongodb:// (e.g. mongodb://localhost:27017).")
            self.url = url

        def __getitem__(self, name):
            return server.db(name)

        def __getattr__(self, name):
            return server.db(name)

        def list_database_names(self):
            return list(server.databases)

    mod.MongoClient = MongoClient
    mod.ASCENDING, mod.DESCENDING = 1, -1
    return mod
