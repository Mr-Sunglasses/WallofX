.PHONY: help init install run run-docker build-docker stop-docker logs-docker clean test

help: ## Show this help message
	@echo "WallOfX - Available commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

init: ## Initialize .env file
	@./scripts/init.sh

install: ## Install dependencies with uv
	uv sync

run: ## Run the bot locally
	uv run run.py

build-docker: ## Build Docker image
	docker-compose build

run-docker: ## Run the bot with Docker
	docker-compose up -d

stop-docker: ## Stop Docker containers
	docker-compose down

restart-docker: stop-docker run-docker ## Restart Docker containers

logs-docker: ## View Docker logs
	docker-compose logs -f

clean: ## Clean generated files
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .venv

.DEFAULT_GOAL := help
