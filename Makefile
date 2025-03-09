.PHONY: up down run run-reload open-api erase-storage refresh-package test test-unit test-integration build-tree help
.DEFAULT_GOAL := help

help:  ## Display this help message
	@awk 'BEGIN {FS = ":.*?## "}; /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

up:  ## Run the application with docker-compose
	docker-compose up --build

down:  ## Stop the application with docker-compose
	docker-compose down

run:  ## Default target - run the application
	uvicorn bookmarker.main:app

run-reload:  ## Run with reload for development
	uvicorn bookmarker.main:app --reload

open-api:  ## Open the OpenAPI documentation in the browser
	open http://localhost:8000/docs

erase-storage:  ## Erase the .storage/ directory with confirmation
	@echo "Are you sure you want to erase the .storage/ directory? [y/N]"; \
	read answer; \
	if [ "$$answer" = "y" ] || [ "$$answer" = "Y" ]; then \
		rm -rf .storage/; \
		echo ".storage/ has been erased."; \
	else \
		echo "Operation cancelled."; \
	fi

refresh-package:  ## Refresh packages (install editable mode and sync)
	uv pip install -e . && uv sync

test:  ## Run all tests with verbose output
	pytest -v

test-unit:  ## Run unit tests with verbose output
	pytest -v -m unit

test-integration:  ## Run integration tests with verbose output
	pytest -v -m integration

build-tree:  ## Build directory tree and save to tree.txt, respecting .gitignore
	@if ! command -v tree >/dev/null 2>&1; then \
		echo "Error: 'tree' command is not installed."; \
		echo "Please install tree using your package manager:"; \
		echo "  sudo apt-get install tree    # Debian/Ubuntu"; \
		echo "  brew install tree            # macOS"; \
		echo "  sudo dnf install tree        # Fedora"; \
		exit 1; \
	fi
	tree --gitignore -I tree.txt > tree.txt