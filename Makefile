.PHONY: install-dev lint format format-check test check build upload clean

VENV = .venv
VENV_READY = $(VENV)/.installed

# --system-site-packages: phpy is not pip-installable, it must already be
# present system-wide (see docker-python3.14-caddy-server's PHPY_ENABLED
# option) — tests only run inside that environment.
#
# A file-based prerequisite (not just a phony target): every other target
# depends on $(VENV_READY), so each one bootstraps the venv on its own if
# missing, and Make skips reinstalling when pyproject.toml hasn't changed.
$(VENV_READY): pyproject.toml
	python3 -m venv --system-site-packages $(VENV)
	$(VENV)/bin/pip install --upgrade pip
	$(VENV)/bin/pip install -e '.[dev]'
	touch $(VENV_READY)

install-dev: $(VENV_READY)

lint: $(VENV_READY)
	$(VENV)/bin/ruff check .

format: $(VENV_READY)
	$(VENV)/bin/ruff format .

format-check: $(VENV_READY)
	$(VENV)/bin/ruff format --check .

test: $(VENV_READY)
	$(VENV)/bin/pytest -v

check: lint format-check test

build: $(VENV_READY)
	$(VENV)/bin/python -m build

upload: build
	$(VENV)/bin/twine upload dist/*

clean:
	rm -rf .venv dist build *.egg-info .pytest_cache .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
