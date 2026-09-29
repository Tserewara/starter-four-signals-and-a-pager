"""The catalog's given behaviour, black-box over HTTP. A port passes these."""

import os
import unittest

import httpx

SERVICE = os.environ.get("SERVICE_URL", "http://localhost:8020")
STORE = os.environ.get("STORE_URL", "http://localhost:9100")


class Contract(unittest.TestCase):
    def setUp(self):
        httpx.delete(f"{STORE}/_control/fault")

    tearDown = setUp

    def test_health(self):
        r = httpx.get(f"{SERVICE}/health")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), {"status": "ok"})

    def test_item_with_its_price(self):
        r = httpx.get(f"{SERVICE}/v1/catalog/sku-7")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), {"sku": "sku-7", "price": 1299, "currency": "BRL"})

    def test_store_failure_is_503(self):
        httpx.put(f"{STORE}/_control/fault", json={"error_every": 1})
        r = httpx.get(f"{SERVICE}/v1/catalog/sku-7")
        self.assertEqual(r.status_code, 503)

    def test_store_recovery(self):
        httpx.put(f"{STORE}/_control/fault", json={"error_every": 1})
        httpx.get(f"{SERVICE}/v1/catalog/sku-7")
        httpx.delete(f"{STORE}/_control/fault")
        self.assertEqual(httpx.get(f"{SERVICE}/v1/catalog/sku-7").status_code, 200)


if __name__ == "__main__":
    unittest.main(verbosity=2)
