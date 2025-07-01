.PHONY: format sort lint

# Variables
ISORT_OPTIONS = --profile black
PROJECT_NAME := mem0ai

# Default target
all: format sort lint

install:
	hatch env create

install_all:
	pip install --requirement requirements-dev.txt
	@echo "Development dependencies installed from requirements-dev.txt"

# Format code with ruff
format:
	hatch run format

# Sort imports with isort
sort:
	hatch run isort mem0/

# Lint code with ruff
lint:
	hatch run lint

docs:
	cd docs && mintlify dev

build:
	hatch build

publish:
	hatch publish

clean:
	rm -rf dist

test:
	hatch run test

test-py-3.9:
	hatch run dev_py_3_9:test

test-py-3.10:
	hatch run dev_py_3_10:test

test-py-3.11:
	hatch run dev_py_3_11:test
