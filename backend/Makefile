.PHONY: install run test test-cov lint format typecheck quality docker-up docker-down

install:
	python -m pip install -e ".[dev]"

run:
	uvicorn alphainvest.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest

test-cov:
	pytest --cov=alphainvest --cov-report=term-missing --cov-report=html

lint:
	ruff check src tests

format:
	ruff format src tests

typecheck:
	mypy src

quality: lint typecheck test-cov

docker-up:
	docker compose up --build -d

docker-down:
	docker compose down
