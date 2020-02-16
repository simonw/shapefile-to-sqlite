# shapefile-to-sqlite

[![PyPI](https://img.shields.io/pypi/v/shapefile-to-sqlite.svg)](https://pypi.org/project/shapefile-to-sqlite/)
[![CircleCI](https://circleci.com/gh/simonw/shapefile-to-sqlite.svg?style=svg)](https://circleci.com/gh/simonw/shapefile-to-sqlite)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/simonw/shapefile-to-sqlite/blob/master/LICENSE)

Load shapefiles into a SQLite (optionally SpatiaLite) database.

## How to install

    $ pip install shapefile-to-sqlite

## How to use

You can run this tool against a shapefile file like so:

    $ shapefile-to-sqlite my.db features.shp

This will load the geometries as GeoJSON in a text column.

If you have SpatiaLite available you can load them as SpatiaLite geometries like this:

    $ shapefile-to-sqlite my.db features.shp --spatialite
