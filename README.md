
# Core Banking Simulator

This a core banking simulator used in vino bank demo. It build with [Quart](https://palletsprojects.com/p/quart/) and [Tortoise ORM](https://tortoise.github.io/). [aerich]() is used for database schema migration.


## Quick Start

```shell

# the easiest way to install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# create virtualenv and install dependencies
uv sync
source .venv/bin/activate

# fix various formatting and import issues automatically
ruff check . --fix

# use pre-commit to ensure only clean code is commiteed
pre-commit install -f

# run test to ensure the basic setup is working
# by default a sqlite in-memory database will be used for testing
pytest -s -v

# Run the server
quart run

```



See the [generated pyproject.toml](pyproject.toml) for more details on the tools and configurations.

## Create datbase for use with applicaiton
The database location and credential are read from ```DATABASE_URL``` in ```.env``` file.

```shell
# create user and database. for PostgreSQL
psql -U postgres

CREATE USER appuser WITH PASSWORD 'password';
CREATE DATABASE database OWNER appuser;


# create .env file
echo 'DATABASE_URL="asyncpg://appuser:password@server:port/database??minsize=2&maxsize=10"' > .env

# run schema migration
source .venv/bin/activate
aerich upgrade

# ready to go!
```
