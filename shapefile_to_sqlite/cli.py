import click
from pathlib import Path
from pyproj import CRS
import pyproj.exceptions
import textwrap
from . import utils

# Have to import these two in this specific order or OS X might segmentation fault!
# https://github.com/simonw/shapefile-to-sqlite/issues/1
from shapely.geometry import shape
import fiona


def validate_crs(ctx, param, value):
    if not value:
        return CRS.from_epsg(4326)
    elif value == "keep":
        return None
    if value.isdigit():
        value = int(value)
    try:
        return CRS.from_user_input(value)
    except pyproj.exceptions.CRSError as e:
        raise click.BadParameter(str(e))


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
@click.option(
    "--crs",
    callback=validate_crs,
    help=(
        "Coordinate Reference System to use in the produced database. "
        "By default data will be projected to WGS-84 - you can use "
        "--crs=keep to use the same projection as the original Shapefile. "
        "To specify a custom CRS use an EPSG integer or an authority string "
        "or a PROJ string or a CRS WKT string."
    ),
)
@click.option("--alter", is_flag=True, help="Add any missing columns")
@click.option("--spatialite", is_flag=True, help="Use SpatiaLite")
@click.option(
    "--spatialite_mod",
    help="Path to SpatiaLite module, for if --spatialite cannot find it automatically",
)
@click.option(
    "-v",
    "--verbose",
    help="Show extra information, including the CRS details",
    is_flag=True,
)
def cli(db_path, shapefile, table, crs, alter, spatialite, spatialite_mod, verbose):
    "Load shapefiles into a SQLite (optionally SpatiaLite) database"
    if verbose and crs:
        print("Output CRS: {}".format(crs))
        print(textwrap.indent(repr(crs), "  "))
    for filepath in shapefile:
        openpath = filepath
        if str(filepath).endswith(".zip"):
            openpath = "zip://{}".format(openpath)
        with fiona.open(openpath) as collection:
            print(openpath)
            shapefile_crs = CRS.from_wkt(collection.crs_wkt) if collection.crs else None
            if shapefile_crs is not None:
                # I need this to be a 'projected' CRS, not a 'bound' CRS
                # https://geopandas.readthedocs.io/en/stable/projections.html#i-get-a-bound-crs
                # Otherwise I get this error:
                # pyproj.exceptions.ProjError: Input is not a transformation.:
                # (Internal Proj Error: proj_normalize_for_visualization: Object
                #  is not a CoordinateOperation created with proj_create_crs_to_crs)
                if shapefile_crs.is_bound:
                    shapefile_crs = shapefile_crs.source_crs
            if verbose and collection.crs:
                print("  Shapefile CRS: {}".format(shapefile_crs))
                print(textwrap.indent(repr(shapefile_crs), "    ").rstrip())
            with click.progressbar(collection) as bar:
                db_table = utils.import_features(
                    db_path,
                    table=table or Path(filepath).stem,
                    features=bar,
                    shapefile_crs=shapefile_crs,
                    target_crs=crs,
                    alter=alter,
                    spatialite=spatialite,
                    spatialite_mod=spatialite_mod,
                )
                num_added = db_table.count
                if verbose:
                    print(
                        "\n\n{} feature{} added to table {}\n".format(
                            num_added, "s" if num_added != 1 else "", db_table.name
                        )
                    )
