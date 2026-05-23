# CNG Workshop Materials

Slides + hands-on notebooks for the **Cloud Native Geospatial** workshop at **CIVIS, Salzburg, 2026**.

Talk page: <https://virtughan.github.io/civis-workshop-eo-2026/>

## Quickstart

```bash
just setup     # uv sync
just prepare   # one-shot: pull Austria buildings → parquet, GeoParquet, FGB, PMTiles
just notebooks # render 01 + 02
just render    # build the full site
just preview   # local live-reload
```

`just prepare` runs once. Upload the four `data/outputs/austria_buildings.*` files to S3 and flip the `BASE` constant at the top of [01_vector.qmd](notebooks/01_vector.qmd) to the bucket URL, the API is identical for local paths and HTTPS.

PMTiles generation requires `tippecanoe` (`brew install tippecanoe`)

## Stack

Python via `uv` (`package = false`), Quarto 1.9+, `just`, `ruff`.

## Deployment

[.github/workflows/publish.yml](.github/workflows/publish.yml) builds and deploys to GitHub Pages on push to `main`.
