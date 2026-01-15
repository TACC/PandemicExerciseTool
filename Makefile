.PHONY: help
help:  ## Display this help screen
	@grep -E '^([a-zA-Z_-]+):.*?## .*$$|^([a-zA-Z_-]+):' $(MAKEFILE_LIST) \
	| awk 'BEGIN {FS = ":.*?## "}; {if ($$2) {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2} else {printf "\033[36m%-30s\033[0m %s\n", $$1, "(no description)"}}'

.PHONY: reset
reset: ## stop containers and delete volumes (FULL DB RESET)
	docker compose -f docker-compose.yml down -v
	docker compose -f docker-compose.yml up -d --build

.PHONY: start
start: ## start
	docker compose -f docker-compose.yml up -d --build

.PHONY: stop
stop: ## stop
	docker compose -f docker-compose.yml down

.PHONY: reset-dev
reset-dev: ## reset dev containers
	docker compose -f docker-compose-dev.yml down -v
	docker compose -f docker-compose-dev.yml up -d --build

.PHONY: start-dev
start-dev: ## start dev environment where frontend components are mounted in container
	docker compose -f docker-compose-dev.yml up -d --build

.PHONY: stop-dev
stop-dev: ## stop dev environment
	docker compose -f docker-compose-dev.yml down
