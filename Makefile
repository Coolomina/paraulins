.PHONY: install dev test test-cov lint format type-check clean run

# Install dependencies
install:
	pdm install

# Install with dev dependencies
dev:
	pdm install -dG dev,test

# Run the application
run:
	pdm run start

# Run tests
test:
	pdm run test

# Run tests with coverage
test-cov:
	pdm run test-cov

# Lint code
lint:
	pdm run lint

# Format code
format:
	pdm run format

# Type check
type-check:
	pdm run type-check

# Clean up
clean:
	rm -rf __pycache__ .pytest_cache .coverage htmlcov
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Setup development environment
setup-dev: install dev
	mkdir -p data/audio data/images

# Run all quality checks
check: lint type-check test

# Help
help:
	@echo "Available commands:"
	@echo "  install     - Install dependencies"
	@echo "  dev         - Install with dev dependencies"
	@echo "  run         - Run the application"
	@echo "  test        - Run tests"
	@echo "  test-cov    - Run tests with coverage"
	@echo "  lint        - Lint code"
	@echo "  format      - Format code"
	@echo "  type-check  - Run type checking"
	@echo "  clean       - Clean up generated files"
	@echo "  setup-dev   - Setup development environment"
	@echo "  check       - Run all quality checks"
