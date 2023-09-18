# gryffen

This project was generated using fastapi_template.

## Poetry

This project uses poetry. It's a modern dependency management
tool.

To run the project use this set of commands:

```bash
poetry install
poetry run python -m gryffen
```

This will start the server on the configured host.

You can find swagger documentation at `/api/docs`.

You can read more about poetry here: https://python-poetry.org/

## Docker

You can start the project with docker using this command:

```bash
docker-compose -f deploy/docker-compose.yml --project-directory . up --build
```

If you want to develop in docker with autoreload add `-f deploy/docker-compose.dev.yml` to your docker command.
Like this:

```bash
docker-compose -f deploy/docker-compose.yml -f deploy/docker-compose.dev.yml --project-directory . up
```

This command exposes the web application on port 8000, mounts current directory and enables autoreload.

But you have to rebuild image every time you modify `poetry.lock` or `pyproject.toml` with this command:

```bash
docker-compose -f deploy/docker-compose.yml --project-directory . build
```

## Project structure

```bash
$ tree "gryffen"
gryffen
├── __init__.py
├── __main__.py
├── conftest.py
├── core
│   ├── __init__.py
│   ├── exchanges
│   │   ├── TDAmeritrade
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── client.py
│   │   │   └── enums.py
│   │   └── __init__.py
│   ├── strategies
│   │   ├── __init__.py
│   │   ├── enum.py
│   │   ├── grid.py
│   │   └── martingale.py
│   └── websocket
│       ├── __init__.py
│       ├── schema.py
│       └── streamer.py
├── db
│   ├── base.py
│   ├── dependencies.py
│   ├── handlers
│   │   ├── __init__.py
│   │   ├── activation.py
│   │   ├── credential.py
│   │   ├── exchange.py
│   │   ├── strategy.py
│   │   └── user.py
│   ├── meta.py
│   ├── migrations
│   │   ├── __init__.py
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions
│   │       ├── 2021-08-16-16-53_819cbf6e030b.py
│   │       ├── 2023-09-12-21-12_c47f5427f323.py
│   │       ├── 2023-09-15-13-08_929422a2c75e.py
│   │       └── __init__.py
│   ├── models
│   │   ├── __init__.py
│   │   ├── activations.py
│   │   ├── credentials.py
│   │   ├── exchanges.py
│   │   ├── positions.py
│   │   ├── strategies.py
│   │   └── users.py
│   └── utils.py
├── logging.py
├── security.py
├── settings.py
├── static
│   └── docs
│       ├── redoc.standalone.js
│       ├── swagger-ui-bundle.js
│       └── swagger-ui.css
├── tests
│   ├── __init__.py
│   └── test_echo.py
└── web
    ├── __init__.py
    ├── api
    │   ├── __init__.py
    │   ├── docs
    │   │   ├── __init__.py
    │   │   └── views.py
    │   ├── echo
    │   │   ├── __init__.py
    │   │   ├── schema.py
    │   │   └── views.py
    │   ├── griffin-ca510.json
    │   ├── monitoring
    │   │   ├── __init__.py
    │   │   └── views.py
    │   ├── router.py
    │   ├── utils.py
    │   └── v1
    │       ├── __init__.py
    │       ├── credential
    │       │   ├── __init__.py
    │       │   ├── schema.py
    │       │   └── views.py
    │       ├── exchange
    │       │   ├── __init__.py
    │       │   ├── schema.py
    │       │   └── views.py
    │       ├── strategy
    │       │   ├── __init__.py
    │       │   ├── schema.py
    │       │   └── views.py
    │       └── user
    │           ├── __init__.py
    │           ├── schema.py
    │           └── views.py
    ├── application.py
    └── lifetime.py
```

## Configuration

This application can be configured with environment variables.

You can create `.env` file in the root directory and place all
environment variables here.

All environment variables should start with "GRYFFEN_" prefix.

For example if you see in your "gryffen/settings.py" a variable named like
`random_parameter`, you should provide the "GRYFFEN_RANDOM_PARAMETER"
variable to configure the value. This behaviour can be changed by overriding `env_prefix` property
in `gryffen.settings.Settings.Config`.

An example of .env file:
```bash
GRYFFEN_RELOAD="True"
GRYFFEN_PORT="8000"
GRYFFEN_ENVIRONMENT="dev"
```

You can read more about BaseSettings class here: https://pydantic-docs.helpmanual.io/usage/settings/

## Pre-commit

To install pre-commit simply run inside the shell:
```bash
pre-commit install
```

pre-commit is very useful to check your code before publishing it.
It's configured using .pre-commit-config.yaml file.

By default it runs:
* black (formats your code);
* mypy (validates types);
* isort (sorts imports in all files);
* flake8 (spots possibe bugs);


You can read more about pre-commit here: https://pre-commit.com/

## Migrations

If you want to migrate your database, you should run following commands:
```bash
# To run all migrations until the migration with revision_id.
alembic upgrade "<revision_id>"

# To perform all pending migrations.
alembic upgrade "head"
```

### Reverting migrations

If you want to revert migrations, you should run:
```bash
# revert all migrations up to: revision_id.
alembic downgrade <revision_id>

# Revert everything.
 alembic downgrade base
```

### Migration generation

To generate migrations you should run:
```bash
# For automatic change detection.
alembic revision --autogenerate

# For empty file generation.
alembic revision
```


## Running tests

If you want to run it in docker, simply run:

```bash
docker-compose -f deploy/docker-compose.yml --project-directory . run --rm api pytest -vv .
docker-compose -f deploy/docker-compose.yml --project-directory . down
```

For running tests on your local machine.
1. you need to start a database.

I prefer doing it with docker:
```
docker run -p "3306:3306" -e "MYSQL_PASSWORD=gryffen" -e "MYSQL_USER=gryffen" -e "MYSQL_DATABASE=gryffen" -e ALLOW_EMPTY_PASSWORD=yes bitnami/mysql:8.0.30
```


2. Run the pytest.
```bash
pytest -vv .
```
