# =============================================================================
# InventoryApp Makefile
# =============================================================================

# Project metadata
PROJECT_NAME := inventory-app
PYTHON_VERSION := 3.11

# Paths
SRC_FILES := *.py

# Commands
UV_CMD := uv
PYTHON_CMD := python3

# Development tools
LINTER := ruff
FORMATTER := ruff
TYPECHECK := mypy
TEST_RUNNER := pytest

# Colors for output
BOLD := \033[1m
GREEN := \033[32m
BLUE := \033[34m
YELLOW := \033[33m
RED := \033[31m
RESET := \033[0m

# =============================================================================
# PHONY TARGETS
# =============================================================================

.PHONY: help install lint typecheck test check-all clean

# =============================================================================
# HELP AND INFORMATION
# =============================================================================

help: ## Show this help message
	@echo "$(BOLD)$(PROJECT_NAME) - Flask Inventory Management$(RESET)"
	@echo ""
	@echo "$(BLUE)Available commands:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(RESET) %s\n", $$1, $$2}'

# =============================================================================
# DEPENDENCY MANAGEMENT
# =============================================================================

install: ## Install all dependencies including dev tools
	@echo "$(BLUE)Installing dependencies...$(RESET)"
	$(UV_CMD) pip install -r requirements.txt
	@echo "$(GREEN)✓ Dependencies installed$(RESET)"

# =============================================================================
# CODE QUALITY TOOLS
# =============================================================================

lint: ## Run linting checks with ruff
	@echo "$(BLUE)Running linting...$(RESET)"
	$(UV_CMD) run $(LINTER) check $(SRC_FILES)
	@echo "$(BLUE)Running format check...$(RESET)"
	$(UV_CMD) run $(FORMATTER) format --check $(SRC_FILES)
	@echo "$(GREEN)✓ Linting passed$(RESET)"

typecheck: ## Run type checking with mypy
	@echo "$(BLUE)Running type checking...$(RESET)"
	$(UV_CMD) run $(TYPECHECK) $(SRC_FILES) --ignore-missing-imports
	@echo "$(GREEN)✓ Type checking passed$(RESET)"

test: ## Run all tests with pytest
	@echo "$(BLUE)Running tests...$(RESET)"
	$(UV_CMD) run $(TEST_RUNNER) tests/ -v
	@echo "$(GREEN)✓ Tests passed$(RESET)"

# =============================================================================
# COMBINED CHECKS
# =============================================================================

check-all: lint typecheck test ## Run all checks (lint, typecheck, test)
	@echo "$(GREEN)✓ All checks passed!$(RESET)"

# =============================================================================
# CLEANUP TARGETS
# =============================================================================

clean: ## Clean up cache files
	@echo "$(BLUE)Cleaning cache files...$(RESET)"
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "$(GREEN)✓ Cache cleaned$(RESET)"
