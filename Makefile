.PHONY: install test test-api test-frontend test-integration run-api run-frontend run dev clean

# Install dependencies
install:
	cd api && uv venv && uv pip install -r requirements.txt
	npm install

# Run all tests
test: test-api test-frontend

# Test API
test-api:
	cd api && uv run pytest test_app.py -v

# Test frontend
test-frontend:
	npm test -- --watchAll=false

# Integration tests (requires API to be running)
test-integration:
	cd api && uv run pytest test_integration.py -v

# Run API server
run-api:
	cd api && uv run python app_mock.py

# Run frontend dev server
run-frontend:
	npm run dev

# Run both servers
dev:
	@echo "Starting API server on http://localhost:5001..."
	@cd api && uv run python app_mock.py &
	@echo "Starting frontend on http://localhost:5173..."
	@npm run dev

# Clean up
clean:
	rm -rf api/__pycache__ api/.pytest_cache
	rm -rf node_modules
	rm -rf dist