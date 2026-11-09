# Shortcuts for common tasks.

.DEFAULT_GOAL := help
.PHONY: help sysml-validate

help: ## List the available targets
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk -F ':.*## ' '{printf "  %-16s %s\n", $$1, $$2}'

MODEL ?= model

sysml-validate: ## Validate the model (default: model/). Set MODEL to validate a different path
	sysml -strict -validate $(MODEL)
