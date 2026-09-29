import logging
import os

import httpx
from fastapi import FastAPI, HTTPException

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("catalog")

STORE_URL = os.environ.get("STORE_URL", "http://localhost:9100")
store = httpx.AsyncClient(base_url=STORE_URL, timeout=5.0)
app = FastAPI(title="catalog", version="1.0.0")


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/v1/catalog/{sku}")
async def catalog(sku: str):
    """One catalog item. Checkout reads the current price from here."""
    try:
        response = await store.get(f"/items/{sku}")
    except httpx.HTTPError as exc:
        log.warning("price store unreachable sku=%s error=%s", sku, exc)
        raise HTTPException(status_code=503, detail="catalog unavailable")
    if response.status_code >= 500:
        log.warning("price store failed sku=%s status=%s", sku, response.status_code)
        raise HTTPException(status_code=503, detail="catalog unavailable")
    item = response.json()
    return {"sku": item["sku"], "price": item["price"], "currency": item["currency"]}
