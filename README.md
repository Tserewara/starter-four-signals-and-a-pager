# Catalog API

This repository contains the catalog API and a small load generator. Start it
with `make up`, run the given tests with `make test`, generate a 100-request
sample with `make load`, and stop it with `make down`.

The API is at `http://localhost:8020`. `GET /v1/catalog/{sku}` returns a
catalog item. The local fault controls are `PUT /_control/fault` with
`error_every`, `latency_ms`, and `busy_ms` fields, and
`DELETE /_control/fault`. `make fault` and `make clear-fault` use them. The
load generator prints request count, error rate, mean latency, and p95.

The service currently has ordinary application logs and no monitoring stack.
It is a containerized API intended to be deployed with the included compose
file.
