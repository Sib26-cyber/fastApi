import os
import unittest
from unittest.mock import patch

import sys
from unittest.mock import MagicMock, patch

# Block real MongoDB connection before any app module is imported.
# This prevents database.py from connecting to Atlas during test collection.
os.environ["MONGO_URI"] = "mongodb://localhost:27017"
_mock_collection = MagicMock()
_mock_db_module = MagicMock()
_mock_db_module.collection = _mock_collection
sys.modules["app.database"] = _mock_db_module

from fastapi.testclient import TestClient
from app.main import app
import app.routes as routes


class DeleteResult:
    def __init__(self, deleted_count: int):
        self.deleted_count = deleted_count


class CursorMock:
    def __init__(self, items):
        self.items = list(items)

    def sort(self, key, order):
        reverse = order == -1
        self.items = sorted(self.items, key=lambda x: x.get(key, ""), reverse=reverse)
        return self

    def skip(self, n):
        self.items = self.items[n:]
        return self

    def limit(self, n):
        self.items = self.items[:n]
        return self

    def __iter__(self):
        return iter(self.items)


class FakeCollection:
    def __init__(self):
        self.data = {
            "1001": {
                "ProductID": "1001",
                "Name": "Notebook",
                "UnitPrice": 10.5,
                "StockQuantity": 5,
                "Description": "Paper notebook",
            },
            "1089": {
                "ProductID": "1089",
                "Name": "Nail",
                "UnitPrice": 2.0,
                "StockQuantity": 20,
                "Description": "Steel nail",
            },
        }

    def _project(self, product, projection):
        if not projection:
            return dict(product)
        if projection.get("_id") == 0:
            return {k: v for k, v in product.items() if k != "_id"}
        return dict(product)

    def find_one(self, query, projection=None):
        pid = query.get("ProductID")
        product = self.data.get(str(pid))
        if not product:
            return None
        return self._project(product, projection)

    def find(self, query=None, projection=None):
        query = query or {}
        items = list(self.data.values())

        if "Name" in query and "$regex" in query["Name"]:
            regex = query["Name"]["$regex"]
            prefix = regex[1:] if regex.startswith("^") else regex
            items = [p for p in items if p["Name"].lower().startswith(prefix.lower())]

        if "ProductID" in query:
            pid_filter = query["ProductID"]
            if "$gte" in pid_filter and "$lte" in pid_filter:
                start = int(pid_filter["$gte"])
                end = int(pid_filter["$lte"])
                items = [p for p in items if start <= int(p["ProductID"]) <= end]

        projected = [self._project(p, projection) for p in items]
        return CursorMock(projected)

    def insert_one(self, product):
        self.data[str(product["ProductID"])] = dict(product)

    def delete_one(self, query):
        pid = str(query.get("ProductID"))
        if pid in self.data:
            del self.data[pid]
            return DeleteResult(1)
        return DeleteResult(0)


class ApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def setUp(self):
        self.fake_collection = FakeCollection()
        self.collection_patcher = patch.object(routes, "collection", self.fake_collection)
        self.collection_patcher.start()

        self.http_patcher = patch.object(routes.requests, "get", autospec=True)
        self.mock_get = self.http_patcher.start()

        class FakeResponse:
            @staticmethod
            def raise_for_status():
                return None

            @staticmethod
            def json():
                return {"rates": {"EUR": 0.9}}

        self.mock_get.return_value = FakeResponse()

    def tearDown(self):
        self.collection_patcher.stop()
        self.http_patcher.stop()

    def test_home(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("message"), "Products API is running")

    def test_health(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("status"), "ok")

    def test_metrics(self):
        response = self.client.get("/metrics")
        self.assertEqual(response.status_code, 200)
        self.assertIn("request_count_total", response.text)

    def test_get_all(self):
        response = self.client.get("/getAll")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_get_single_product(self):
        response = self.client.get("/getSingleProduct/1001")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("ProductID"), "1001")

    def test_add_new(self):
        payload = {
            "ProductID": "2001",
            "Name": "New Product",
            "UnitPrice": 11.99,
            "StockQuantity": 3,
            "Description": "Created in test",
        }
        response = self.client.post("/addNew", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("message"), "Product added successfully")

    def test_delete_one(self):
        response = self.client.delete("/deleteOne/1001")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("message"), "Product deleted successfully")

    def test_starts_with(self):
        response = self.client.get("/startsWith/n")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_paginate(self):
        response = self.client.get("/paginate?start_id=1000&end_id=2000&page=1")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_convert(self):
        response = self.client.get("/convert/1089")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload.get("ProductID"), "1089")
        self.assertIn("UnitPriceEUR", payload)


if __name__ == "__main__":
    unittest.main()
