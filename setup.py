from setuptools import setup
import os

VERSION = "0.4.2"


def get_long_description():
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
        encoding="utf8",
    ) as fp:
        return fp.read()


setup(
    name="shapefile-to-sqlite",
    description="Load shapefiles into a SQLite (optionally SpatiaLite) database",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Simon Willison",
    url="https://github.com/simonw/shapefile-to-sqlite",
    project_urls={
        "Issues": "https://github.com/simonw/shapefile-to-sqlite/issues",
        "CI": "https://github.com/simonw/shapefile-to-sqlite/actions",
        "Changelog": "https://github.com/simonw/shapefile-to-sqlite/releases",
    },
    license="Apache License, Version 2.0",
    version=VERSION,
    packages=["shapefile_to_sqlite"],
    entry_points="""
        [console_scripts]
        shapefile-to-sqlite=shapefile_to_sqlite.cli:cli
    """,
    install_requires=["sqlite-utils>=2.2", "Shapely", "Fiona", "pyproj"],
    extras_require={"test": ["pytest"]},
    tests_require=["shapefile-to-sqlite[test]"],
)
