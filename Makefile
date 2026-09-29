COMPOSE = docker compose -f harness/compose.yaml
.PHONY: up down contract load fault fault-latency clear-fault rehearse rehearse-latency pages reload logs

# The service, the price store, background traffic, Prometheus, Alertmanager,
# the pager and Grafana.
up:
	$(COMPOSE) up -d --build

down:
	$(COMPOSE) down

# The given behaviour, black-box. Passes on the starter; must still pass after.
contract:
	$(COMPOSE) run --rm --build contract

# 100 requests, ten at a time, then one summary line.
load:
	$(COMPOSE) run --rm --build tools python3 loadgen.py --count 100

# Every fifth price-store call fails (and every call takes 250 ms).
fault:
	curl -fsS -X PUT http://localhost:9100/_control/fault -H 'Content-Type: application/json' -d '{"error_every":5,"latency_ms":250}'; echo

# Every price-store call takes 2.5 seconds, and none fails.
fault-latency:
	curl -fsS -X PUT http://localhost:9100/_control/fault -H 'Content-Type: application/json' -d '{"latency_ms":2500}'; echo

clear-fault:
	curl -fsS -X DELETE http://localhost:9100/_control/fault; echo

# Fault on, background traffic running: seconds until the pager gets a page.
rehearse:
	$(COMPOSE) run --rm --build tools python3 rehearse.py error

rehearse-latency:
	$(COMPOSE) run --rm --build tools python3 rehearse.py latency

# Every notification the pager has received.
pages:
	@curl -fsS http://localhost:9099/pages | python3 -m json.tool

# Reread monitoring/rules/ without restarting Prometheus.
reload:
	curl -fsS -X POST http://localhost:9090/-/reload

logs:
	$(COMPOSE) logs -f service
