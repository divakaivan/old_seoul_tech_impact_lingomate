DOCKER_COMPOSE_FILE=docker-compose.yaml

.DEFAULT_GOAL := help

.PHONY: help
help:  ## Show this help message
	@echo ""
	@echo "Usage: make [option]"
	@echo ""
	@echo "Options:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""

.PHONY: setup
setup:  ## Install requirements, build docker services and prepare elasticsearch index
	pip install -r requirements.txt && docker compose -f $(DOCKER_COMPOSE_FILE) build && python prepare_index.py

.PHONY: db
db:  ## Setup database
	python db.py

.PHONY: start
start:  ## Start docker services (detached mode)
	docker compose -f $(DOCKER_COMPOSE_FILE) up -d

.PHONY: stop
stop:  ## Stop docker services
	docker compose -f $(DOCKER_COMPOSE_FILE) stop