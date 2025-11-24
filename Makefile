.PHONY: install dev format lint type-check test test-watch run start pre-commit hooks

PYTHON ?= python
APP_MODULE ?= apps.api.main:app

install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt

dev: install pre-commit

pre-commit:
	pre-commit install

format:
	black apps config graph rag state tools observability tests
	isort apps config graph rag state tools observability tests

lint:
	ruff check .

type-check:
	mypy apps config graph rag state tools

test:
	pytest tests

test-watch:
	pytest tests --maxfail=1 --disable-warnings -q

run:
	uvicorn $(APP_MODULE) --reload --port 8000

start: run
