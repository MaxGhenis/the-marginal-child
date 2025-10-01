.PHONY: install install-dev run test format lint clean docker-build docker-run docker-stop

# Install dependencies
install:
	pip install -e .

# Install with development dependencies
install-dev:
	pip install -e ".[dev]"
	pre-commit install

# Run Streamlit app
run:
	streamlit run app.py

# Run tests
test:
	pytest tests/ -v --cov=. --cov-report=term-missing

# Format code
format:
	black . --line-length 79
	isort . --profile black --line-length 79

# Lint code
lint:
	black --check --line-length 79 .
	isort --check-only --profile black --line-length 79 .
	flake8 . --max-line-length=79 --extend-ignore=E203,W503
	mypy . --ignore-missing-imports

# Clean up
clean:
	rm -rf __pycache__ .streamlit/ .pytest_cache/ .coverage htmlcov/ .mypy_cache/
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

# Docker commands
docker-build:
	docker-compose build

docker-run:
	docker-compose up -d

docker-stop:
	docker-compose down

docker-logs:
	docker-compose logs -f

# Development workflow
dev: install-dev format lint test

# Deployment
deploy: format lint test
	@echo "Ready for deployment!"