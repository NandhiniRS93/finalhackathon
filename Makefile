# Makefile for Xray Test Automation

.PHONY: help install install-dev test test-cov lint format type-check security clean build upload-test upload docs sample-doc run-sample

# Default target
help:
	@echo "Available commands:"
	@echo "  install      Install package dependencies"
	@echo "  install-dev  Install package with development dependencies"
	@echo "  test         Run test suite"
	@echo "  test-cov     Run test suite with coverage report"
	@echo "  lint         Run code linting"
	@echo "  format       Format code with black"
	@echo "  type-check   Run type checking with mypy"
	@echo "  security     Run security checks"
	@echo "  clean        Clean build artifacts"
	@echo "  build        Build package"
	@echo "  upload-test  Upload to test PyPI"
	@echo "  upload       Upload to PyPI"
	@echo "  docs         Generate documentation"
	@echo "  sample-doc   Generate sample Word document"
	@echo "  run-sample   Test with sample document (dry run)"

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install pytest pytest-cov black flake8 mypy safety bandit build twine

test:
	python -m pytest tests/ -v

test-cov:
	python -m pytest tests/ -v --cov=src --cov-report=html --cov-report=term-missing

lint:
	flake8 src tests --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 src tests --count --exit-zero --max-complexity=10 --max-line-length=100 --statistics

format:
	black src tests samples

format-check:
	black --check --diff src tests samples

type-check:
	mypy src --ignore-missing-imports

security:
	safety check --requirements requirements.txt
	bandit -r src

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build

upload-test: build
	python -m twine upload --repository testpypi dist/*

upload: build
	python -m twine upload dist/*

docs:
	@echo "Documentation files:"
	@echo "  README.md - Main documentation"
	@echo "  docs/API.md - API reference"
	@echo "  docs/TROUBLESHOOTING.md - Troubleshooting guide"
	@echo "  samples/README.md - Sample files documentation"

sample-doc:
	python samples/sample_test_scenarios.py

run-sample: sample-doc
	python cli.py -f ./samples/sample_test_scenarios.docx --dry-run -v

# Development workflow targets
dev-setup: install-dev
	@echo "Development environment setup complete!"
	@echo "Next steps:"
	@echo "  1. Copy .env.example to .env and configure"
	@echo "  2. Run 'make run-sample' to test with sample data"

ci-test: lint format-check type-check test security
	@echo "All CI checks passed!"

# Quick development targets
quick-test:
	python -m pytest tests/test_config.py -v

quick-lint:
	flake8 src --select=E9,F63,F7,F82

# Git hooks
pre-commit: format-check lint type-check quick-test
	@echo "Pre-commit checks passed!"

# Release preparation
prepare-release: clean ci-test build
	@echo "Release preparation complete!"
	@echo "Built packages in dist/:"
	@ls -la dist/