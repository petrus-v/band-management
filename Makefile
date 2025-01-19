.PHONY: clean clean-build clean-pyc lint test setup help
.DEFAULT_GOAL := help

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

install: ## install python project dependencies
	uv sync

setup:
	uv run anyblok_createdb -c app.cfg || uv run anyblok_updatedb -c app.cfg

setup-tests: ## install python project dependencies for tests
	uv run anyblok_createdb --with-demo -c app.test.cfg || uv run anyblok_updatedb -c app.test.cfg

test:
	ANYBLOK_CONFIG_FILE=app.test.cfg uv run pytest -v -s src/


run:
	uv run gunicorn_anyblok_uvicorn --anyblok-configfile app.cfg -w 4 -b 0.0.0.0:5000 --timeout 5


clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +
