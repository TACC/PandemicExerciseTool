.PHONY: help
help:  ## Display this help screen
	@grep -E '^([a-zA-Z_-]+):.*?## .*$$|^([a-zA-Z_-]+):' $(MAKEFILE_LIST) \
	| awk 'BEGIN {FS = ":.*?## "}; {if ($$2) {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2} else {printf "\033[36m%-30s\033[0m %s\n", $$1, "(no description)"}}'

.PHONY: start
start: ## start
	docker compose -f docker-compose.yml up -d --build

.PHONY: stop
stop: ## stop
	docker compose -f docker-compose.yml down

.PHONY: start-dev
start-dev: ## start dev environment where frontend components are mounted in container
	docker compose -f docker-compose-dev.yml up -d --build

.PHONY: stop-dev
stop-dev: ## stop dev environment
	docker compose -f docker-compose-dev.yml down

.PHONY: start-dash
start-dash: ## start with Dash frontend instead of React
	docker compose -f docker-compose-dash.yml up -d --build

.PHONY: stop-dash
stop-dash: ## stop Dash frontend environment
	docker compose -f docker-compose-dash.yml down

.PHONY: dash-dev
dash-dev: ## run Dash frontend locally for development (backend must be running)
	@echo "Starting Dash frontend in development mode..."
	@echo "Make sure backend is running first with 'make start' or 'make start-dev'"
	@echo "Frontend will be available at: http://localhost:8050"
	cd dash_frontend && python app.py
