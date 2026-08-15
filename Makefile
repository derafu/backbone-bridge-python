.PHONY: install-dev lint format format-check test check build upload clean

# --system-site-packages: phpy is not pip-installable, it must already be
# present system-wide (see docker-python3.14-caddy-server's PHPY_ENABLED
# option) — tests only run inside that environment.
install-dev:
	python3 -m venv --system-site-packages .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -e '.[dev]'

lint:
	.venv/bin/ruff check .

format:
	.venv/bin/ruff format .

format-check:
	.venv/bin/ruff format --check .

test:
	.venv/bin/pytest -v

check: lint format-check test

build:
	.venv/bin/python -m build

upload: build
	.venv/bin/twine upload dist/*

clean:
	rm -rf dist build *.egg-info .pytest_cache .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
