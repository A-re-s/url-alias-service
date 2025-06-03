.PHONY: all test lint format isort black docker-build docker-run clean

all: format lint test

run:
	uvicorn src.main:app

test:
	python -m pytest --disable-warnings

lint:
	pylint src

black:
	black src --config pyproject.toml

isort:
	isort src

format: isort black

clean:
	rm -rf __pycache__ .pytest_cache */__pycache__