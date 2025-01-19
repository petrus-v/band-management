[![codecov](https://codecov.io/gh/petrus-v/band-management/graph/badge.svg?token=IXBBQODJEJ)](https://codecov.io/gh/petrus-v/band-management)

# Band Management

An application helping managing **band** focused around
**band's music scores**.


## Setup development environment

> **note**: I'm using linux machine with `build-essential` and postgresql client installed.

* clone the project

```bash
git clone https://github.com/petrus-v/band-management
```

* setup git pre-commit hooks outside the current env to launch linter at git commit

```bash
uv tool install --with pre-commit-uv pre-commit
uvx pre-commit install --install-hooks
```

* you have postgresql access and your user account is able to create database
  like `createdb testdb`, if not you'll need to tweak app.test.cfg file according
  your settings.

* Install dependency and setup db

```bash
uv run anyblok_createdb -c app.test.cfg
```

* launch test

```bash
ANYBLOK_CONFIG_FILE=app.test.cfg uv run pytest -v -s src/
```

* launch linters

```bash
uvx pre-commit run --all-files
```