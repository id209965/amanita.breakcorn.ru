# Makefile for video player automated testing

.PHONY: help install test test-unit test-integration test-performance test-fast test-slow test-all
.PHONY: test-coverage test-html test-parallel server clean lint format check-deps

# Default target
help:
	@echo "Available targets:"
	@echo "  install         - Install dependencies"
	@echo "  test           - Run all tests"
	@echo "  test-unit      - Run unit tests only"
	@echo "  test-integration - Run integration tests only"
	@echo "  test-performance - Run performance tests only"
	@echo "  test-fast      - Run fast tests only (exclude slow)"
	@echo "  test-slow      - Run slow tests only"
	@echo "  test-coverage  - Run tests with coverage report"
	@echo "  test-html      - Run tests with HTML report"
	@echo "  test-parallel  - Run tests in parallel"
	@echo "  server         - Start development server"
	@echo "  clean          - Clean generated files"
	@echo "  lint           - Run linting"
	@echo "  format         - Format code"
	@echo "  check-deps     - Check for dependency updates"

# Installation
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install black flake8 mypy safety

# Basic test targets
test:
	python run_tests.py

test-unit:
	python run_tests.py --type unit -v

test-integration:
	python run_tests.py --type integration -v --server

test-performance:
	python run_tests.py --type performance -v --server

test-fast:
	python run_tests.py --type fast -v

test-slow:
	python run_tests.py --type slow -v --server

test-memory:
	python run_tests.py --type memory -v --server

test-browser:
	python run_tests.py --type browser -v --server

# Enhanced test targets
test-all:
	python run_tests.py --server -v

test-coverage:
	python run_tests.py --coverage --html --server -v

test-html:
	python run_tests.py --html --server -v

test-parallel:
	python run_tests.py --parallel --server -v

test-headless:
	python run_tests.py --headless --server -v

test-firefox:
	python run_tests.py --browser firefox --server -v

# Development server
server:
	python -m http.server 8000

server-bg:
	python -m http.server 8000 &

# Quality checks
lint:
	flake8 tests/ --max-line-length=120 --ignore=E203,W503

format:
	black tests/ --line-length=120

type-check:
	mypy tests/ --ignore-missing-imports

check-deps:
	safety check -r requirements.txt
	pip list --outdated

# Cleanup
clean:
	rm -rf reports/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf screenshots/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# CI simulation
ci-test:
	@echo "Simulating CI environment..."
	CI=true python run_tests.py --headless --coverage --html -v

# Quick development test
dev-test:
	python run_tests.py --type fast --no-headless -v

# Full test suite for release
release-test:
	make clean
	python run_tests.py --server --coverage --html --parallel -v
	make lint
	make check-deps

# Docker-based testing (if Docker is available)
docker-test:
	docker run --rm -v $(PWD):/app -w /app python:3.11 make install test-headless

# Continuous testing (requires entr or similar)
watch-test:
	ls tests/**/*.py | entr -c make test-fast
