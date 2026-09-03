import unittest
from fastapi.testclient import TestClient

from api import app


class GivenBehaviourTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.client.delete("/_control/fault")

    def test_catalog_returns_price(self):
        response = self.client.get("/v1/catalog/sku-1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["currency"], "BRL")

    def test_fault_control_can_make_errors(self):
        self.client.put("/_control/fault", json={"error_every": 2})
        self.assertEqual(self.client.get("/v1/catalog/sku-1").status_code, 200)
        self.assertEqual(self.client.get("/v1/catalog/sku-1").status_code, 503)


if __name__ == "__main__":
    unittest.main()
