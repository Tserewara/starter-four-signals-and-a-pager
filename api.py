import asyncio
import logging
import time
from dataclasses import dataclass

from fastapi import FastAPI, HTTPException

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("catalog-api")
app = FastAPI(title="catalog-api", version="1.0.0")


@dataclass
class FaultState:
    error_every: int = 0
    latency_ms: int = 0
    busy_ms: int = 0
    calls: int = 0


fault = FaultState()


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/v1/catalog/{sku}")
async def catalog(sku: str):
    fault.calls += 1
    started = time.perf_counter()
    if fault.latency_ms:
        await asyncio.sleep(fault.latency_ms / 1000)
    if fault.busy_ms:
        end = time.perf_counter() + fault.busy_ms / 1000
        while time.perf_counter() < end:
            pass
    if fault.error_every and fault.calls % fault.error_every == 0:
        log.warning("catalog fault sku=%s call=%d", sku, fault.calls)
        raise HTTPException(status_code=503, detail="catalog dependency unavailable")
    elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
    log.info("catalog response sku=%s latency_ms=%s", sku, elapsed_ms)
    return {"sku": sku, "price": 1299, "currency": "BRL"}


@app.put("/_control/fault")
async def set_fault(body: dict):
    fault.error_every = int(body.get("error_every", 0))
    fault.latency_ms = int(body.get("latency_ms", 0))
    fault.busy_ms = int(body.get("busy_ms", 0))
    fault.calls = 0
    log.info("fault configuration changed error_every=%s latency_ms=%s busy_ms=%s", fault.error_every, fault.latency_ms, fault.busy_ms)
    return {"error_every": fault.error_every, "latency_ms": fault.latency_ms, "busy_ms": fault.busy_ms}


@app.delete("/_control/fault")
async def clear_fault():
    fault.error_every = fault.latency_ms = fault.busy_ms = fault.calls = 0
    return {"cleared": True}
