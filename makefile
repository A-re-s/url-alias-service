-include .env

API_PORT ?= 8000

.PHONY: all test lint format isort black docker-build docker-run clean

all: format lint test

run:
	uvicorn src.main:app --host 0.0.0.0 --port $(API_PORT)

test:
	python -m pytest --disable-warnings

lint:
	pylint src

black:
	black src --config pyproject.toml

isort:
	isort src

format: isort black

docker-build:
	docker build -t user_service .

docker-run: docker-build
	docker run --env-file .env --rm -it -p ${API_PORT}:8000 user_service

docker-run-detached: docker-build
	docker run --env-file .env --rm -d -p ${API_PORT}:8000 user_service

clean:
	rm -rf __pycache__ .pytest_cache */__pycache__