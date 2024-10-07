.PHONY: help
help:  ## Display this help screen
	@grep -E '^([a-zA-Z_-]+):.*?## .*$$|^([a-zA-Z_-]+):' $(MAKEFILE_LIST) \
	| awk 'BEGIN {FS = ":.*?## "}; {if ($$2) {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2} else {printf "\033[36m%-30s\033[0m %s\n", $$1, "(no description)"}}'

.PHONY: build
build: ## build dev
	docker compose -f docker-compose-dev.yml build

.PHONY: start
start: ## start dev environment where client code changes will be automatically updated on running client
	docker compose -f docker-compose-dev.yml up

.PHONY: stop
stop: ## stop dev
	docker compose -f docker-compose-dev.yml down
