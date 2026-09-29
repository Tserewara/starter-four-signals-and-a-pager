# Catalog

The catalog service, and the world around it. Checkout calls
`GET /v1/catalog/{sku}` for the current price; the service reads it from a
price store.

```
service/     the catalog: Python and FastAPI
harness/     the price store (faked), background traffic, Prometheus,
             Alertmanager, a stand-in pager and Grafana
contract/    black-box tests of what the catalog answers
monitoring/  rules/ and dashboards/, empty: Prometheus and Grafana load
             whatever you put there
```

## Running it

`make up` starts everything, and `make down` stops it. Docker is the only
thing you need on your machine.

| Where | What |
|---|---|
| `http://localhost:8020` | the catalog service |
| `http://localhost:9090` | Prometheus. It scrapes `GET /metrics` on the service every 5 seconds and evaluates every `*.yml` in `monitoring/rules/`. |
| `http://localhost:9093` | Alertmanager. Every alert goes to the pager. |
| `http://localhost:9099/pages` | the pager: every notification it received |
| `http://localhost:3000` | Grafana, with Prometheus as its data source. It loads every dashboard JSON in `monitoring/dashboards/`. |

Right now the service writes plain log lines and has no `/metrics`, so
Prometheus shows its target as down.

Timing, for anything you measure against a page: Prometheus scrapes and
evaluates rules every 5 seconds, and Alertmanager groups alerts by name and
waits 2 seconds before the first notification of a group. `make up` rebuilds
the service after you change it; Grafana rereads `monitoring/dashboards/`
every 10 seconds.

## Commands

- `make load` sends 100 requests, ten at a time, and prints
  `requests=100 errors=0 error_rate=0.000 mean_ms=… p95_ms=…`.
  Background traffic (10 requests a second) runs all the time anyway.
- `make fault` makes every fifth price-store call fail and every call take
  250 ms. `make fault-latency` makes every call take 2.5 seconds, with no
  failures. `make clear-fault` turns both off.
- `make rehearse` and `make rehearse-latency` run a paging rehearsal: they
  wait until no alert has fired for 200 seconds (giving up after 500 with
  `alerts keep firing with no fault on`), turn the fault on, and print
  `fault=error first_page=<alert> seconds=<n>` with the page's annotations,
  or `no page within 300s`. They clear the fault when they finish.
- `make pages` prints what the pager has received.
- `make reload` makes Prometheus reread `monitoring/rules/`.
- `make contract` runs the contract tests against the service.
- `make logs` follows the service's log.

## Porting the service

The service is Python and FastAPI; you can write it in another language. It
must listen on port 8000 inside its container (the harness publishes it as 8020), read the price store's address from `STORE_URL`,
and answer the routes in `contract/openapi.yaml`. Build it from
`service/Dockerfile` (or point `harness/compose.yaml` at your directory),
then run `make contract` until it passes. Everything else talks to it over
HTTP, so the rest works unchanged.
