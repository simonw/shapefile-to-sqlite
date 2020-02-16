import click
from pathlib import Path
from . import utils

# Have to import these two in this specific order or OS X might segmentation fault!
# https://github.com/simonw/shapefile-to-sqlite/issues/1
from shapely.geometry import shape
import fiona


@click.command()
@click.argument(
    "db_path",
    type=click.Path(file_okay=True, dir_okay=False, allow_dash=False),
    required=True,
)
@click.argument(
    "shapefile",
    type=click.Path(file_okay=True, exists=True, dir_okay=False, allow_dash=True),
    nargs=-1,
)
@click.option("--table", help="Table to load data into")
@click.option("--pk", help="Column to use as a primary key")
@click.option("--alter", is_flag=True, help="Add any missing columns")
@click.option("--spatialite", is_flag=True, help="Use SpatiaLite")
@click.option(
    "--spatialite_mod",
    help="Path to SpatiaLite module, for if --spatialite cannot find it automatically",
)
def cli(db_path, table, shapefile, pk, alter, spatialite, spatialite_mod):
    "Load shapefiles into a SQLite (optionally SpatiaLite) database"
    for filepath in shapefile:
        openpath = filepath
        if str(filepath).endswith(".zip"):
            openpath = "zip://{}".format(openpath)
        with fiona.open(openpath) as collection:
            with click.progressbar(collection) as bar:
                utils.import_features(
                    db_path,
                    table=table or Path(filepath).stem,
                    features=bar,
                    pk=pk,
                    alter=alter,
                    spatialite=spatialite,
                    spatialite_mod=spatialite_mod,
                )
