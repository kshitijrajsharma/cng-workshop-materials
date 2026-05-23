default:
    @just --list

setup:
    uv sync
    uv run pre-commit install

prepare:
    uv run python scripts/prepare.py

lint:
    uv run ruff check --fix .
    uv run ruff format .
    uv run ty check scripts

render:
    quarto render

preview:
    quarto preview

publish:
    quarto publish gh-pages

notebooks:
    uv run quarto render notebooks/01_vector.qmd
    uv run quarto render notebooks/02_raster.qmd
    quarto convert notebooks/01_vector.qmd
    quarto convert notebooks/02_raster.qmd

build: notebooks render
