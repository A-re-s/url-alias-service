-include .env

API_PORT ?= 8000

.PHONY: all test lint format isort black docker-build docker-run docker-build-test docker-test clean

all: format lint test

run:
	uvicorn --app-dir src main:app --host 0.0.0.0 --port ${API_PORT}

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

docker-build-test:
	docker build --target test -t user_service .

docker-test: docker-build-test
	docker run --rm user_service

docker-run: docker-build
	docker run --env-file .env --rm -i -p 8000:${API_PORT} user_service

docker-run-detached: docker-build
	docker run --env-file .env --rm -d -p 8000:${API_PORT} user_service

docker-compose-run:
	docker-compose up

clean:
	rm -rf __pycache__ .pytest_cache */__pycache__
