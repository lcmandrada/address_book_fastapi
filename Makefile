.PHONY: clean clean-test clean-pyc clean-build

PACKAGE = src

# Remove artifacts
clean: clean-pyc clean-test

# Remove Python artifacts
clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

# Remove test artifacts
clean-test:
	rm -fr test-reports/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

# Run formatters, checkers and tests
verify: format lint static test

# Run formatters without changes
format-check:
	poetry run isort --check ${PACKAGE} tests
	poetry run black --check ${PACKAGE} tests

# Format imports and code
format:
	poetry run isort ${PACKAGE} tests
	poetry run black ${PACKAGE} tests

# Check static typing
static:
	poetry run mypy ${PACKAGE}

# Check lint
lint:
	poetry run flake8 ${PACKAGE} tests

# Run unit tests
test:
	poetry run pytest

# Run unit tests with coverage output to terminal
test-cov:
	poetry run pytest --cov=${PACKAGE} --cov-report=term

# Run unit tests with coverage output to HTML
test-cov-html:
	poetry run pytest --cov=${PACKAGE} --cov-report=term --cov-report=html

# Clean and install project
install: clean
	poetry install

# Run app
run:
	poetry run python src/address_book_fastapi.py

# Build a Docker image
docker-build:
	docker build . -t address_book_fastapi

# Run app in a container
docker-run:
	docker run -it address_book_fastapi

# Open an interactive shell inside a container
docker-sh:
	docker run -it --entrypoint /bin/sh address_book_fastapi

# Remove stopped containers
docker-rm:
	docker rm $$(docker ps -a -f status=exited -q)

# Remove dangling resources
docker-prune:
	docker system prune

# Remove dangling and unused resources
# Useful for recovering Docker storage space
docker-prune-all:
	docker system prune -a
