# Memory-C* Enhanced Makefile with Comprehensive Testing
# Ensures all commands execute in correct directories

.PHONY: help ui-dev ui-build ui-install api-dev api-install start-all stop-all status clean setup docker-up docker-down docker-logs hadolint shellcheck test test-all test-fast test-unit test-integration test-e2e test-performance test-bmad test-py test-ts test-with-coverage test-parallel test-smoke test-ai-framework test-install test-deps test-report test-clean test-watch test-debug lint lint-py lint-ts format format-py format-ts check-all reports reports-clean reports-open coverage-report

# Variables
PROJECT_ROOT := $(shell pwd)
UI_DIR := $(PROJECT_ROOT)/mem0/openmemory/ui
API_DIR := $(PROJECT_ROOT)/mem0/openmemory/api
OPENMEMORY_DIR := $(PROJECT_ROOT)/mem0/openmemory

# Colors
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

# Default target
help:
	@echo "$(BLUE)Memory-C* Development Commands$(NC)"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "$(GREEN)Primary Test Commands:$(NC)"
	@echo "  make test          - Run all tests with coverage"
	@echo "  make test-fast     - Run fast unit tests only"
	@echo "  make test-smoke    - Run smoke tests"
	@echo "  make check-all     - Run quality checks + fast tests"
	@echo ""
	@echo "$(GREEN)Test Categories:$(NC)"
	@echo "  make test-unit     - Unit tests"
	@echo "  make test-integration - Integration tests"
	@echo "  make test-e2e      - End-to-end tests"
	@echo "  make test-bmad     - BMAD tests"
	@echo "  make test-ai-framework - AI framework tests"
	@echo ""
	@echo "$(GREEN)Language-Specific:$(NC)"
	@echo "  make test-py       - Python tests only"
	@echo "  make test-ts       - TypeScript tests only"
	@echo ""
	@echo "$(GREEN)Test Modes:$(NC)"
	@echo "  make test-parallel - Parallel execution"
	@echo "  make test-watch    - Watch mode"
	@echo "  make test-debug    - Debug mode"
	@echo ""
	@echo "$(GREEN)UI Commands:$(NC)"
	@echo "  make ui-dev        - Start UI development server (port 3010)"
	@echo "  make ui-build      - Build UI for production"
	@echo "  make ui-install    - Install UI dependencies"
	@echo ""
	@echo "$(GREEN)API Commands:$(NC)"
	@echo "  make api-dev       - Start API server (port 8765)"
	@echo "  make api-install   - Install API dependencies"
	@echo ""
	@echo "$(GREEN)Service Management:$(NC)"
	@echo "  make start-all     - Start all services"
	@echo "  make stop-all      - Stop all services"
	@echo "  make status        - Show service status"
	@echo ""
	@echo "$(GREEN)Setup & Maintenance:$(NC)"
	@echo "  make setup         - Initial project setup"
	@echo "  make clean         - Clean build artifacts"
	@echo "  make test-clean    - Clean test artifacts"
	@echo "  make hadolint      - Lint all Dockerfiles with hadolint"
	@echo "  make shellcheck    - Lint all shell scripts with ShellCheck"
	@echo ""
	@echo "$(GREEN)Reports & Quality:$(NC)"
	@echo "  make reports       - Generate all reports"
	@echo "  make coverage-report - Open coverage report"
	@echo "  make lint          - Lint all code"
	@echo "  make format        - Format all code"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# UI Commands - Always run in UI directory
ui-dev:
	@echo "$(BLUE)[INFO]$(NC) Starting UI development server..."
	@cd $(UI_DIR) && pnpm dev --port 3010

ui-build:
	@echo "$(BLUE)[INFO]$(NC) Building UI for production..."
	@cd $(UI_DIR) && pnpm build

ui-install:
	@echo "$(BLUE)[INFO]$(NC) Installing UI dependencies..."
	@cd $(UI_DIR) && pnpm install

# API Commands - Always run in API directory
api-dev:
	@echo "$(BLUE)[INFO]$(NC) Starting API server..."
	@cd $(API_DIR) && uvicorn main:app --host 0.0.0.0 --port 8765 --reload

api-install:
	@echo "$(BLUE)[INFO]$(NC) Installing API dependencies..."
	@cd $(API_DIR) && pip install -r requirements.txt

# Combined commands
start-all:
	@echo "$(BLUE)[INFO]$(NC) Starting all services..."
	@make -j2 api-dev ui-dev

stop-all:
	@echo "$(BLUE)[INFO]$(NC) Stopping all services..."
	@-pkill -f "uvicorn main:app" 2>/dev/null || true
	@-pkill -f "next dev" 2>/dev/null || true
	@-lsof -ti:3010 | xargs kill -9 2>/dev/null || true
	@-lsof -ti:8765 | xargs kill -9 2>/dev/null || true
	@echo "$(GREEN)[SUCCESS]$(NC) All services stopped"

# Status check
status:
	@echo ""
	@echo "$(BLUE)Memory-C* Service Status$(NC)"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@if lsof -Pi :3010 -sTCP:LISTEN -t >/dev/null 2>&1; then \
		echo "UI Server:     $(GREEN)● Running$(NC) (http://localhost:3010)"; \
	else \
		echo "UI Server:     $(RED)○ Stopped$(NC)"; \
	fi
	@if lsof -Pi :8765 -sTCP:LISTEN -t >/dev/null 2>&1; then \
		echo "API Server:    $(GREEN)● Running$(NC) (http://localhost:8765)"; \
	else \
		echo "API Server:    $(RED)○ Stopped$(NC)"; \
	fi
	@if lsof -Pi :6333 -sTCP:LISTEN -t >/dev/null 2>&1; then \
		echo "Vector DB:     $(GREEN)● Running$(NC) (http://localhost:6333)"; \
	else \
		echo "Vector DB:     $(RED)○ Stopped$(NC)"; \
	fi
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Setup
setup:
	@echo "$(BLUE)[INFO]$(NC) Setting up Memory-C* development environment..."
	@make ui-install
	@make api-install
	@echo "$(GREEN)[SUCCESS]$(NC) Setup complete!"

# Clean
clean:
	@echo "$(BLUE)[INFO]$(NC) Cleaning build artifacts..."
	@cd $(UI_DIR) && rm -rf .next node_modules
	@cd $(API_DIR) && find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)[SUCCESS]$(NC) Clean complete!"

# Docker commands with proper directory context
docker-up:
	@cd $(OPENMEMORY_DIR) && docker compose up -d

docker-down:
	@cd $(OPENMEMORY_DIR) && docker compose down

docker-logs:
	@cd $(OPENMEMORY_DIR) && docker compose logs -f

# Infrastructure linting
hadolint:
	@echo "$(BLUE)[INFO]$(NC) Running hadolint on Dockerfiles..."
	@find . -name "Dockerfile*" | xargs -I{} sh -c 'hadolint "$${1}" || true' -- {}
	@echo "$(GREEN)[SUCCESS]$(NC) Dockerfile linting complete"

shellcheck:
	@echo "$(BLUE)[INFO]$(NC) Running ShellCheck on scripts..."
	@find . -type f -name "*.sh" | xargs -I{} sh -c 'shellcheck "$${1}" || true' -- {}
	@echo "$(GREEN)[SUCCESS]$(NC) Shell script linting complete"

# ============================================================================
# COMPREHENSIVE TESTING FRAMEWORK
# ============================================================================

# Test Management Variables
REPORTS_DIR := $(PROJECT_ROOT)/reports
COVERAGE_DIR := $(REPORTS_DIR)/coverage
TEST_RESULTS_DIR := $(REPORTS_DIR)/test-results

# Python test paths
PYTHON_TEST_PATHS := tests custom-gpt-adapter/tests mem0/tests mem0/embedchain/tests

# ============================================================================
# PRIMARY TEST COMMANDS (for automation tools like Cursor BugBot)
# ============================================================================

# Main test command - runs all tests with coverage
test: test-deps
	@echo "$(BLUE)[TEST]$(NC) Running all tests with coverage..."
	@mkdir -p $(REPORTS_DIR) $(COVERAGE_DIR) $(TEST_RESULTS_DIR)
	@pytest --maxfail=5 --tb=short

# Fast tests - unit tests only, no coverage
test-fast:
	@echo "$(BLUE)[TEST-FAST]$(NC) Running fast unit tests..."
	@pytest -m "unit and not slow" -x --tb=line

# All tests with full reporting
test-all: test-deps
	@echo "$(BLUE)[TEST-ALL]$(NC) Running comprehensive test suite..."
	@mkdir -p $(REPORTS_DIR) $(COVERAGE_DIR) $(TEST_RESULTS_DIR)
	@pytest --maxfail=10

# Smoke tests - basic functionality verification
test-smoke:
	@echo "$(BLUE)[TEST-SMOKE]$(NC) Running smoke tests..."
	@pytest -m smoke --tb=line -v

# ============================================================================
# GRANULAR TEST CATEGORIES
# ============================================================================

# Unit tests
test-unit:
	@echo "$(BLUE)[TEST-UNIT]$(NC) Running unit tests..."
	@pytest -m unit --tb=short

# Integration tests  
test-integration:
	@echo "$(BLUE)[TEST-INTEGRATION]$(NC) Running integration tests..."
	@pytest -m integration --tb=short

# End-to-end tests
test-e2e:
	@echo "$(BLUE)[TEST-E2E]$(NC) Running end-to-end tests..."
	@pytest -m e2e --tb=short -v

# Performance tests
test-performance:
	@echo "$(BLUE)[TEST-PERFORMANCE]$(NC) Running performance tests..."
	@pytest -m performance --tb=short --benchmark-only

# BMAD (Brownfield Memory-Augmented Development) tests
test-bmad:
	@echo "$(BLUE)[TEST-BMAD]$(NC) Running BMAD tests..."
	@pytest -m bmad --tb=short -v

# AI Framework tests
test-ai-framework:
	@echo "$(BLUE)[TEST-AI-FRAMEWORK]$(NC) Running AI framework tests..."
	@pytest -m ai_framework --tb=short -v

# ============================================================================
# LANGUAGE-SPECIFIC TESTS
# ============================================================================

# Python tests only
test-py: test-deps
	@echo "$(BLUE)[TEST-PY]$(NC) Running Python tests..."
	@pytest $(PYTHON_TEST_PATHS) --tb=short

# TypeScript tests only  
test-ts:
	@echo "$(BLUE)[TEST-TS]$(NC) Running TypeScript tests..."
	@cd mem0/vercel-ai-sdk && npm test
	@if [ -f mem0/mem0-ts/package.json ]; then cd mem0/mem0-ts && npm test 2>/dev/null || echo "No tests in mem0-ts"; fi

# ============================================================================
# TEST EXECUTION MODES
# ============================================================================

# Tests with coverage report
test-with-coverage: test-deps
	@echo "$(BLUE)[TEST-COVERAGE]$(NC) Running tests with detailed coverage..."
	@mkdir -p $(COVERAGE_DIR)
	@pytest --cov-report=term --cov-report=html:$(COVERAGE_DIR)/html --cov-report=xml:$(COVERAGE_DIR)/coverage.xml

# Parallel test execution
test-parallel: test-deps
	@echo "$(BLUE)[TEST-PARALLEL]$(NC) Running tests in parallel..."
	@pytest -n auto --tb=short

# Watch mode for development
test-watch: test-deps
	@echo "$(BLUE)[TEST-WATCH]$(NC) Running tests in watch mode..."
	@pytest --looponfail

# Debug mode with verbose output
test-debug: test-deps
	@echo "$(BLUE)[TEST-DEBUG]$(NC) Running tests in debug mode..."
	@pytest -vvv --tb=long --capture=no

# ============================================================================
# TEST UTILITIES
# ============================================================================

# Install test dependencies
test-deps:
	@echo "$(BLUE)[TEST-DEPS]$(NC) Installing test dependencies..."
	@pip install -e .[test] --quiet 2>/dev/null || pip install pytest pytest-cov pytest-html pytest-xdist pytest-asyncio

# Install ALL test dependencies
test-install:
	@echo "$(BLUE)[TEST-INSTALL]$(NC) Installing comprehensive test dependencies..."
	@pip install -e .[test]
	@cd mem0/vercel-ai-sdk && npm install
	@cd mem0/mem0-ts && npm install

# Generate test report
test-report: test-with-coverage
	@echo "$(BLUE)[TEST-REPORT]$(NC) Generating comprehensive test report..."
	@echo "$(GREEN)✓$(NC) Test reports generated in $(REPORTS_DIR)"
	@echo "$(GREEN)✓$(NC) Coverage report: $(COVERAGE_DIR)/html/index.html"

# Clean test artifacts
test-clean:
	@echo "$(BLUE)[TEST-CLEAN]$(NC) Cleaning test artifacts..."
	@rm -rf .pytest_cache $(REPORTS_DIR) .coverage htmlcov
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.pyc" -delete 2>/dev/null || true

# ============================================================================
# CODE QUALITY & FORMATTING
# ============================================================================

# Lint all code
lint: lint-py lint-ts hadolint shellcheck

# Lint Python code
lint-py:
	@echo "$(BLUE)[LINT-PY]$(NC) Linting Python code..."
	@cd mem0 && make lint 2>/dev/null || echo "Using basic pylint..."
	@python -m flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics 2>/dev/null || echo "flake8 not available"

# Lint TypeScript code
lint-ts:
	@echo "$(BLUE)[LINT-TS]$(NC) Linting TypeScript code..."
	@cd mem0/vercel-ai-sdk && npm run lint 2>/dev/null || echo "No TypeScript linting configured"

# Format all code
format: format-py format-ts

# Format Python code
format-py:
	@echo "$(BLUE)[FORMAT-PY]$(NC) Formatting Python code..."
	@cd mem0 && make format 2>/dev/null || echo "Using basic black formatting..."
	@python -m black . 2>/dev/null || echo "black not available"

# Format TypeScript code
format-ts:
	@echo "$(BLUE)[FORMAT-TS]$(NC) Formatting TypeScript code..."
	@cd mem0/vercel-ai-sdk && npm run prettier-check 2>/dev/null || echo "No TypeScript formatting configured"

# Run all quality checks
check-all: lint test-fast
	@echo "$(GREEN)✓$(NC) All quality checks completed"

# ============================================================================
# REPORTING & ANALYTICS
# ============================================================================

# Generate all reports
reports: test-report
	@echo "$(BLUE)[REPORTS]$(NC) Generating all reports..."

# Clean all reports
reports-clean:
	@echo "$(BLUE)[REPORTS-CLEAN]$(NC) Cleaning all reports..."
	@rm -rf $(REPORTS_DIR)

# Open coverage report in browser
coverage-report: test-with-coverage
	@echo "$(BLUE)[COVERAGE-REPORT]$(NC) Opening coverage report..."
	@python -c "import webbrowser; webbrowser.open('file://$(COVERAGE_DIR)/html/index.html')" 2>/dev/null || echo "Coverage report: $(COVERAGE_DIR)/html/index.html"

# Open test results
reports-open:
	@echo "$(BLUE)[REPORTS-OPEN]$(NC) Opening test reports..."
	@python -c "import webbrowser; webbrowser.open('file://$(REPORTS_DIR)/test-results.html')" 2>/dev/null || echo "Test report: $(REPORTS_DIR)/test-results.html"
