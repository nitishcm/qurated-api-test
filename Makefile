.PHONY: init format

init:
	poetry install --with dev --no-root

format:
	poetry run ruff format

run:
	poetry run uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
