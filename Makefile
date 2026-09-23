PROJECT=bgym_signals
.PHONY: up down test load fault fault-latency clear-fault logs

up:
	COMPOSE_PROJECT_NAME=$(PROJECT) docker compose up -d --build

down:
	COMPOSE_PROJECT_NAME=$(PROJECT) docker compose down

test:
	COMPOSE_PROJECT_NAME=$(PROJECT) docker compose exec api python3 -m unittest discover -s tests -v

load:
	COMPOSE_PROJECT_NAME=$(PROJECT) docker compose run --rm loadgen python3 loadgen.py --count 100

fault:
	curl -fsS -X PUT http://localhost:8020/_control/fault -H 'Content-Type: application/json' -d '{"error_every":5,"latency_ms":250}'

# Slow responses only, 2.5s each: over the SLO's two-second bar.
fault-latency:
	curl -fsS -X PUT http://localhost:8020/_control/fault -H 'Content-Type: application/json' -d '{"latency_ms":2500}'

clear-fault:
	curl -fsS -X DELETE http://localhost:8020/_control/fault

logs:
	COMPOSE_PROJECT_NAME=$(PROJECT) docker compose logs -f api
