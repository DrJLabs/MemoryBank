# MemoryBank Enhanced Makefile
# Ensures all commands execute in correct directories

.PHONY: help ui-dev ui-build ui-install api-dev api-install start-all stop-all status clean setup

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
	@echo "$(BLUE)MemoryBank Development Commands$(NC)"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
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
	@echo "$(BLUE)MemoryBank Service Status$(NC)"
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
	@echo "$(BLUE)[INFO]$(NC) Setting up MemoryBank development environment..."
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