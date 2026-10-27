# Shortcuts for common tasks. Each target is a thin wrapper; see README.md for details.

COMPOSE := docker compose -f sysml-api/compose.yaml

.DEFAULT_GOAL := help
.PHONY: help setup api-up api-down api-logs publish lint

help: ## List the available targets
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk -F ':.*## ' '{printf "  %-10s %s\n", $$1, $$2}'

setup: ## Create or update the Python environment
	uv sync

api-up: ## Build and start the SysML v2 API server
	$(COMPOSE) up -d --build

api-down: ## Stop the API server
	$(COMPOSE) down

api-logs: ## Follow the API server logs
	$(COMPOSE) logs -f api

MODEL ?= model

publish: ## Publish the model (default: the model/ directory): make publish [MODEL=model/foo.sysml] [PROJECT=Foo]
	uv run python -m ada.publish $(MODEL) $(if $(PROJECT),--project "$(PROJECT)")

lint: ## Run linters on the codebase
	uv run ruff check --fix
	uv run ruff format