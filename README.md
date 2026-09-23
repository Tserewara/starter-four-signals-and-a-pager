# Catalog API

The catalog API and a small load generator. `make up` starts it, `make test` runs the given tests, `make load` sends a 100-request sample, and `make down` stops it.

The API is at `http://localhost:8020`, and `GET /v1/catalog/{sku}` returns one catalog item. The fault controls are `PUT /_control/fault`, which takes `error_every`, `latency_ms` and `busy_ms`, and `DELETE /_control/fault`, which clears them; `make fault` turns on failing calls with a little extra latency, `make fault-latency` makes every call take 2.5 seconds without failing, and `make clear-fault` turns both off. The load generator sends its requests one after another, so with the latency fault on a 100-request `make load` takes about four minutes; it keeps traffic flowing while you watch the alerts. The load generator prints the request count, error rate, mean latency and p95.

Right now the service has plain application logs and no monitoring. It's a containerized API meant to be deployed with the included compose file.
