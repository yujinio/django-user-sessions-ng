.DEFAULT_GOAL := help

.PHONY: help
help: ## Display this help screen
	@grep -E '^[a-z.A-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

test: export DJANGO_SETTINGS_MODULE=tests.settings
test: ## Run tests
	@echo "--- Running all tests ---"
	@uv run pytest
	@echo "--- Finished running all tests ---"

migrations: export DJANGO_SETTINGS_MODULE=tests.settings
migrations: ## Create new migrations
	@echo "--- Creating new migrations ---"
	@uv run python django-admin makemigrations
	@echo "--- Finished creating new migrations ---"

build: ## Build distribution
	@echo "--- Building distribution ---"
	@uv build
	@echo "--- Finished building distribution ---"
