from shapely.geometry import shape
import fiona
import sqlite_utils
import itertools
import os

# I used this to debug a segmentation fault:
# import faulthandler
# faulthandler.enable()


SPATIALITE_PATHS = (
    "/usr/lib/x86_64-linux-gnu/mod_spatialite.so",
    "/usr/local/lib/mod_spatialite.dylib",
)


class SpatiaLiteError(Exception):
    pass


import json


def import_features(
    db_path,
    table,
    features,
    pk=None,
    alter=False,
    spatialite=False,
    spatialite_mod=None,
):
    db = sqlite_utils.Database(db_path)

    def yield_features():
        for feature in features:
            feature.pop("type")
            feature.update(feature.pop("properties") or {})
            if spatialite:
                feature["geometry"] = shape(feature["geometry"]).wkt
            yield feature

    features_iter = yield_features()

    conversions = {}
    if spatialite_mod:
        spatialite = True
    if spatialite:
        lib = spatialite_mod or find_spatialite()
        if not lib:
            raise SpatiaLiteError("Could not find SpatiaLite module")
        init_spatialite(db, lib)
        if table not in db.table_names():
            # Create the table, using detected column types
            first_100 = list(itertools.islice(features_iter, 0, 100))
            features_iter = itertools.chain(first_100, features_iter)
            column_types = sqlite_utils.suggest_column_types(first_100)
            column_types.pop("geometry")
            db[table].create(column_types, pk=pk)
            ensure_table_has_geometry(db, table)
        conversions = {"geometry": "GeomFromText(?, 4326)"}

    if pk:
        db[table].upsert_all(features_iter, conversions=conversions, pk=pk, alter=alter)
    else:
        db[table].insert_all(features_iter, conversions=conversions, alter=alter)
    return db[table]


def find_spatialite():
    for path in SPATIALITE_PATHS:
        if os.path.exists(path):
            return path
    return None


def init_spatialite(db, lib):
    db.conn.enable_load_extension(True)
    db.conn.load_extension(lib)
    # Initialize SpatiaLite if not yet initialized
    if "spatial_ref_sys" in db.table_names():
        return
    db.conn.execute("select InitSpatialMetadata(1)")


def ensure_table_has_geometry(db, table):
    if "geometry" not in db[table].columns_dict:
        db.conn.execute(
            "SELECT AddGeometryColumn(?, 'geometry', 4326, 'GEOMETRY', 2);", [table]
        )


def has_ids(features):
    return all(f.get("id") is not None for f in features)
