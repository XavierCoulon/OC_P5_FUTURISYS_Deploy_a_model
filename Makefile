# Development commands
.PHONY: format lint check test setup-pre-commit

# Set up pre-commit hooks
setup-pre-commit:
	pre-commit install

# Format code with black and isort
format:
	black app/
	isort app/

# Lint code with flake8
lint:
	flake8 app/

# Check code formatting without making changes
check:
	black --check app/
	isort --check-only app/
	flake8 app/

# Run tests
test:
	pytest

# Run all checks (format check + lint + tests)
check-all: check test

# Format and then run all checks
format-and-check: format check-all
