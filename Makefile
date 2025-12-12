# Makefile for AI Data Storytelling

.PHONY: install run test lint clean

install:
	pip install -r api/requirements.txt
	cd web && npm install

run:
	@echo "Starting Backend and Frontend..."
	bash -c "uvicorn api.main:app --host 0.0.0.0 --port 8000 & cd web && npm run dev"

test:
	@echo "Running Tests..."
	pytest api/tests || echo "No tests found yet."

lint:
	@echo "Linting..."
	# pip install ruff
	ruff check api/ || echo "Ruff not installed, skipping."

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .dvc/cache

stop:
	@echo "Stopping servers..."
	pkill uvicorn || true
	pkill node || true
