.PHONY: help install install-dev lint format test test-unit test-integration test-cov run clean

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	pip install -r requirements.txt

install-dev: ## Install development dependencies
	pip install -r requirements-dev.txt

lint: ## Run ruff linting
	ruff check .

format: ## Format code with ruff
	ruff format .

check-format: ## Check if code is formatted correctly
	ruff format --check .

test: ## Run all tests with pytest
	python -m pytest tests/ -v

test-unit: ## Run unit tests only
	python -m pytest tests/ -v -m "not integration"

test-integration: ## Run integration tests only
	python -m pytest tests/ -v -m "integration"

test-chart: ## Run chart tests only
	python -m pytest tests/test_chart.py -v

test-app: ## Run app tests only
	python -m pytest tests/test_app.py -v

test-cov: ## Run tests with coverage
	python -m pytest tests/ -v --cov=src/diabetes_tracker --cov-report=html --cov-report=term-missing --cov-fail-under=80

test-cov-unit: ## Run unit tests with coverage
	python -m pytest tests/ -v -m "not integration" --cov=src/diabetes_tracker --cov-report=html --cov-report=term-missing

test-fast: ## Run tests quickly (no coverage, minimal output)
	python -m pytest tests/ -x --tb=short

test-debug: ## Run tests with debug output
	python -m pytest tests/ -v -s --tb=long

security: ## Run security checks
	bandit -r . -f json -o bandit-report.json || true
	safety check --json --output safety-report.json || true

run: ## Run the Flask application
	python main.py

run-dev: ## Run the Flask application in development mode
	FLASK_ENV=development FLASK_DEBUG=1 python main.py

clean: ## Clean up generated files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -f bandit-report.json
	rm -f safety-report.json
	rm -rf .mypy_cache

ci: ## Run all CI checks locally
	make lint
	make check-format
	make test-cov
	make security

setup: ## Initial setup for development
	make install-dev
	make format
	make test

test-watch: ## Run tests in watch mode (requires pytest-watch)
	ptw tests/ -- -v

test-html: ## Generate HTML test report
	python -m pytest tests/ --html=reports/test_report.html --self-contained-html

test-xml: ## Generate XML test report for CI
	python -m pytest tests/ --junitxml=reports/test_results.xml

# Database commands
init-db: ## Initialize PostgreSQL database
	python src/diabetes_tracker/init_db.py

migrate-csv: ## Migrate CSV data to PostgreSQL
	python archive/migrate_csv_to_db.py

check-db: ## Check database connection
	python archive/test_db_connection.py

test-gpt: ## Test GPT API integration
	python archive/test_gpt_integration.py

diagnose-db: ## Run detailed database connection diagnostics
	python archive/diagnose_db_connection.py

setup-db: ## Complete database setup (init + migrate if CSV exists)
	make init-db
	@if [ -d "data" ] && [ -f "data/users.csv" ]; then \
		echo "CSV data found. Running migration..."; \
		make migrate-csv; \
	else \
		echo "No CSV data found. Database is ready for new data."; \
	fi 