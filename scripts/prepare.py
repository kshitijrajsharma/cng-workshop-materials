"""Pull every building in Austria from Overture, emit parquet, GeoParquet, FGB, PMTiles."""

import subprocess
from pathlib import Path

import duckdb
import geopandas as gpd

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

XMIN, YMIN, XMAX, YMAX = 9.5, 46.3, 17.2, 49.0

OVERTURE = "s3://overturemaps-us-west-2/release/2026-04-15.0/theme=buildings/type=building/*"

PARQUET = OUT / "austria_buildings.parquet"
GEOPARQUET = OUT / "austria_buildings.geo.parquet"
FGB = OUT / "austria_buildings.fgb"
PMTILES = OUT / "austria_buildings.pmtiles"


def connect() -> duckdb.DuckDBPyConnection:
    con = duckdb.connect()
    con.execute("INSTALL spatial; LOAD spatial;")
    con.execute("INSTALL httpfs; LOAD httpfs;")
    con.execute("SET s3_region='us-west-2';")
    return con


def write_raw_parquet(con: duckdb.DuckDBPyConnection) -> None:
    con.execute(
        f"""
        COPY (
            SELECT id, names.primary AS name, class, subtype, height, num_floors, geometry
            FROM read_parquet('{OVERTURE}', hive_partitioning=1)
            WHERE bbox.xmin BETWEEN {XMIN} AND {XMAX}
              AND bbox.ymin BETWEEN {YMIN} AND {YMAX}
        ) TO '{PARQUET}' (FORMAT PARQUET, COMPRESSION ZSTD);
        """
    )
    print(f"parquet      {PARQUET}  ({PARQUET.stat().st_size / 1e6:.1f} MB)")


def write_geoparquet() -> None:
    gpd.read_parquet(PARQUET).to_parquet(GEOPARQUET, write_covering_bbox=True, compression="zstd")
    print(f"geoparquet   {GEOPARQUET}  ({GEOPARQUET.stat().st_size / 1e6:.1f} MB)")


def write_fgb(con: duckdb.DuckDBPyConnection) -> None:
    FGB.unlink(missing_ok=True)
    con.execute(
        f"""
        COPY (SELECT * FROM read_parquet('{PARQUET}'))
        TO '{FGB}'
        WITH (FORMAT GDAL, DRIVER 'FlatGeobuf');
        """
    )
    print(f"fgb          {FGB}  ({FGB.stat().st_size / 1e6:.1f} MB)")


def write_pmtiles() -> None:
    geojsonl = OUT / "austria_buildings.geojsonl"
    subprocess.run(
        ["ogr2ogr", "-f", "GeoJSONSeq", str(geojsonl), str(PARQUET)],
        check=True,
    )
    subprocess.run(
        [
            "tippecanoe",
            "-zg",
            "--drop-densest-as-needed",
            "--force",
            "-o",
            str(PMTILES),
            str(geojsonl),
        ],
        check=True,
    )
    geojsonl.unlink()
    print(f"pmtiles      {PMTILES}  ({PMTILES.stat().st_size / 1e6:.1f} MB)")


def main() -> None:
    con = connect()
    write_raw_parquet(con)
    write_geoparquet()
    write_fgb(con)
    write_pmtiles()


if __name__ == "__main__":
    main()
