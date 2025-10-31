[![codecov](https://codecov.io/gh/petrus-v/band-management/graph/badge.svg?token=IXBBQODJEJ)](https://codecov.io/gh/petrus-v/band-management)

# Band Management

An application helping managing **band** focused around
**band's music scores**.


## Prerequisites
> **note**: I'm using linux machine with `build-essential`.

- [Setup uv](https://github.com/astral-sh/uv) – used for managing dependencies
- [Setup PostgreSQL](https://www.postgresql.org/download/) – required for database setup

> **MacOS**: You may need additional dependencies in order to setup the database
```bash
# Install WeasyPrint (includes required dependencies)
brew install weasyprint

# Restart PostgreSQL service
brew services restart postgresql
```

## Setup development environment

- clone the project:
```bash
git clone https://github.com/petrus-v/band-management
```
- setup git pre-commit hooks outside the current env to launch linter at git commit

```bash
uv tool install --with pre-commit-uv pre-commit
uvx pre-commit install --install-hooks
```

-  Install dependencies
```bash
make install
```

-  Setup database with demo data
```bash
make setup-demo
```

- Setup tests database  with demo data
```bash
make setup-tests
```

- Run tests
```bash
make test
```

- Regenerate translations
```bash
make translations
make compile-translations
```

- Start the application
```bash
make run
```

- launch linters

```bash
uvx pre-commit run --all-files
```


You may want to import music brainz data (`work` table) [downloaded from here](
  https://data.metabrainz.org/pub/musicbrainz/data/json-dumps/) to populate the music catalog.

```bash
uv run musicbrainz-importer -c app.cfg  --limit 30000 --insert-buffer 1000 ~/path/to/work 
```

## Create a new release

We are using [bump-my-version](https://pypi.org/project/bump-my-version/) to bump
patch / minor / major version and add the git tag. At the moment changelog and
github release are done manually. we have no changelog file yet.
