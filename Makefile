# Image Descriptor Bot - Development Makefile

.PHONY: help install test test-all test-unit test-integration test-e2e test-coverage test-pytest run clean lint

# Default target
help:
	@echo "🤖 Image Descriptor Bot - Development Commands"
	@echo "=============================================="
	@echo ""
	@echo "Setup:"
	@echo "  install       Install dependencies"
	@echo ""
	@echo "Testing:"
	@echo "  test          Run all tests (custom runner)"
	@echo "  test-all      Run all tests (custom runner)"
	@echo "  test-unit     Run unit tests only"
	@echo "  test-integration Run integration/e2e tests only"
	@echo "  test-e2e      Run end-to-end tests only (alias for test-integration)"
	@echo "  test-pytest   Run all tests using pytest"
	@echo "  test-coverage Run tests with coverage report"
	@echo ""
	@echo "Development:"
	@echo "  run           Run the bot locally"
	@echo "  lint          Run code linting"
	@echo "  clean         Clean temporary files"

# Install dependencies
install:
	@echo "📦 Installing dependencies..."
	pip install -r requirements.txt

# Test targets - All use the updated simple runner
test: test-all

test-all:
	@echo "🧪 Running all tests (custom runner)..."
	python test_runner.py --type all

test-unit:
	@echo "🧪 Running unit tests only..."
	python test_runner.py --type unit

test-integration:
	@echo "🧪 Running integration/e2e tests..."
	python test_runner.py --type e2e

test-e2e: test-integration

# Pytest-based testing
test-pytest:
	@echo "🧪 Running all tests with pytest..."
	python -m pytest tests/ -v -p no:asyncio -p no:pytest_asyncio

test-coverage:
	@echo "📊 Running tests with coverage..."
	python run_tests.py --coverage

# Development targets
run:
	@echo "🚀 Starting Image Descriptor Bot locally..."
	@if [ ! -f .env ]; then \
		echo "❌ .env file not found. Please create it with TELEGRAM_TOKEN and OPENAI_API_KEY"; \
		exit 1; \
	fi
	PYTHONPATH=. PYTHONUNBUFFERED=1 python -u src/local.py

lint:
	@echo "🔍 Running code linting..."
	@command -v flake8 >/dev/null 2>&1 || pip install flake8
	flake8 src/ tests/ --max-line-length=100 --ignore=E501,W503

clean:
	@echo "🧹 Cleaning temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -delete
	rm -rf .coverage htmlcov/

# Quick development cycle
dev: clean install test 