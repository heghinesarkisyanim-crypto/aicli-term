.PHONY: install install-dev run test lint format clean help

PYTHON := python3
PIP    := pip

help:
	@echo "aicli - Natural Language to Linux Commands"
	@echo ""
	@echo "Usage:"
	@echo "  make install      Install aicli (production)"
	@echo "  make install-dev  Install with dev dependencies"
	@echo "  make run CMD=...  Run aicli with a command"
	@echo "  make test         Run all tests"
	@echo "  make lint         Check code style"
	@echo "  make format       Auto-format code"
	@echo "  make clean        Remove build artifacts"

install:
	$(PIP) install -e .

install-dev:
	$(PIP) install -e ".[dev]"

run:
	$(PYTHON) -m aicli $(CMD)

test:
	pytest tests/ -v

test-cov:
	pytest tests/ -v --cov=aicli --cov-report=term-missing

lint:
	ruff check aicli/ tests/

format:
	ruff format aicli/ tests/

clean:
	rm -rf build/ dist/ *.egg-info .pytest_cache .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete
