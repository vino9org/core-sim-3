
# Welcome to Python project

This project is set up Python project with dev tooling pre-configured

* ruff
* mypy
* VS Code support

## Setup

The easiest way to get started is use [Visual Studio Code with devcontainer](https://code.visualstudio.com/docs/devcontainers/containers)

[rye](https://github.com/astral-sh/rye) is the blazing fast python project manager tool. Install it first before proceeding.


## Quick Start

```shell

# the easiest way to install Rye
curl -sSf https://rye.astral.sh/get | bash


cd my_project_directory

# create virtualenv and install dependencies
rye sync



# fix various formatting and import issues automatically
rye run ruff check . --fix



# use pre-commit to ensure only clean code is commiteed
rye run pre-commit install -f

# run test to ensure the basic setup is working
pytest -s -v

# Hack away!!

```



See the [generated pyproject.toml](pyproject.toml) for more details on the tools and configurations.
