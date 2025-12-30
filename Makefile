.PHONY: install install-dev test test-cov run-pipeline run-dashboard clean check-maturity \
        lint format type-check audit-code quality env-clean venv venv-install \
        test-kpi-parity analytics-sync analytics-run gradle-build upgrade-gradle vscode-envfile-info help

# ------------------------------------------------------------------------------
# Installation targets
# ------------------------------------------------------------------------------

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt -r dev-requirements.txt

# ------------------------------------------------------------------------------
# Testing targets
# ------------------------------------------------------------------------------

test:
	pytest

test-cov:
	pytest --cov=python --cov-report=html --cov-report=term

# ------------------------------------------------------------------------------
# Code quality targets
# ------------------------------------------------------------------------------

lint:
	@echo "Running pylint..."
	pylint python --exit-zero
	@echo "\nRunning flake8..."
	flake8 python --exit-zero
	@echo "\nRunning ruff check..."
	ruff check python --exit-zero

format:
	@echo "Running black..."
	black python
	@echo "\nRunning isort..."
	isort python

type-check:
	@echo "Running mypy..."
	mypy python --ignore-missing-imports

audit-code: lint type-check test-cov
	@echo "\n✅ Code audit complete: linting, type checking, and tests"

quality: format lint type-check test
	@echo "\n✅ Full quality check complete"

# ------------------------------------------------------------------------------
# Operational targets
# ------------------------------------------------------------------------------

run-pipeline:
	python scripts/run_data_pipeline.py

run-dashboard:
	streamlit run streamlit_app.py

check-maturity:
	python repo_maturity_summary.py

# ------------------------------------------------------------------------------
# Python environment management
# ------------------------------------------------------------------------------

env-clean:
	rm -rf .venv .venv-1

venv:
	$(MAKE) env-clean
	python3 -m venv .venv
	@echo "Activate with: source .venv/bin/activate"

venv-install: venv
	@echo "Setting up virtualenv with project dependencies..."
	. .venv/bin/activate && \
	  pip install --upgrade pip && \
	  pip install -r requirements.txt -r dev-requirements.txt

# KPI parity test (dual-engine governance)
test-kpi-parity:
	. .venv/bin/activate && pytest -q tests/test_kpi_parity.py

# Analytics validation and execution
analytics-run:
	. .venv/bin/activate && python3 run_complete_analytics.py

analytics-sync:
	. .venv/bin/activate && python3 tools/check_kpi_sync.py --print-json

# ------------------------------------------------------------------------------
# Gradle / Java helpers
# ------------------------------------------------------------------------------

# Usage:
#   make gradle-build JAVA_HOME=$(/usr/libexec/java_home -v 21)
gradle-build:
	@echo "Running Gradle build with JAVA_HOME=$$JAVA_HOME"
	JAVA_HOME=$$JAVA_HOME PATH=$$JAVA_HOME/bin:$$PATH ./gradlew clean build

upgrade-gradle:
	@echo "Upgrading Gradle wrapper to 9.1.0 for Java 25 support"
	./gradlew wrapper --gradle-version=9.1.0
	./gradlew wrapper

# ------------------------------------------------------------------------------
# VS Code .env warning info
# ------------------------------------------------------------------------------

vscode-envfile-info:
	@echo "To enable .env file loading in VS Code terminals, set 'python.terminal.useEnvFile' to true in your settings."

# ------------------------------------------------------------------------------
# Cleanup
# ------------------------------------------------------------------------------

clean:
	rm -rf __pycache__ .pytest_cache
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	rm -rf .coverage htmlcov
	find . -type d -name ".mypy_cache" -exec rm -rf {} +

# ------------------------------------------------------------------------------
# Help
# ------------------------------------------------------------------------------

help:
	@echo "Available targets:"
	@echo "  make install          - Install production dependencies"
	@echo "  make install-dev      - Install dev + prod dependencies"
	@echo "  make test             - Run tests"
	@echo "  make test-cov         - Run tests with coverage report"
	@echo "  make lint             - Run linters (pylint, flake8, ruff)"
	@echo "  make format           - Auto-format code (black, isort)"
	@echo "  make type-check       - Run mypy type checking"
	@echo "  make audit-code       - Lint + type-check + coverage"
	@echo "  make quality          - Full quality check (format + lint + type + test)"
	@echo "  make run-pipeline     - Run the data pipeline"
	@echo "  make run-dashboard    - Run Streamlit dashboard"
	@echo "  make check-maturity   - Check repository maturity"
	@echo "  make env-clean        - Remove local virtualenvs"
	@echo "  make venv             - Create a fresh .venv (no packages)"
	@echo "  make venv-install     - Create .venv and install requirements"
	@echo "  make test-kpi-parity  - Run KPI parity tests (Python vs SQL)"
	@echo "  make analytics-run    - Run complete analytics pipeline"
	@echo "  make analytics-sync   - Validate KPI sync and health"
	@echo "  make gradle-build     - Run Gradle build with provided JAVA_HOME"
	@echo "  make upgrade-gradle   - Upgrade Gradle wrapper to 9.1.0"
	@echo "  make clean            - Clean up temporary files"
	@echo "  make help             - Show this help message"
