"""
image_date_organizer.cli
~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2019 Sander Bollen
:license: BSD-3-clause
"""
import pathlib
import click

from .organize import organize
from .utils import get_package_version


def path_callback(ctx, param, value):
    """Click fallback function for generating pathlib.Path instances"""
    return pathlib.Path(value)


@click.command(name="image_date_organizer")
@click.version_option(get_package_version())
@click.argument("source", type=click.Path(readable=True),
                callback=path_callback)
@click.option("-d", "--dest",
              type=click.Path(dir_okay=True, file_okay=False, writable=True),
              required=True, callback=path_callback,
              help="Destination directory")
@click.option("--remove-source", is_flag=True,
              help="Enable to remove the source files after import was "
                   "completed.")
@click.option("-l", "--log-level",
              type=click.Choice(["ERROR", "WARNING", "INFO", "DEBUG"]),
              default="INFO")
def main(source: pathlib.Path, dest: pathlib.Path, remove_source: bool,
         log_level: str = "INFO"):
    """
    Import images from source and organize them into destination by date.

    source may be either a single file or a directory. In case of the latter,
    the source directory will be searched recursively for image files.

    Images will be organized first by year, then by month, and lastly by day.

    Dates will be taken from EXIF or XMP metadata fields, if available.
    If no such metadata fields are available, we will fall back to mtime as
    the source of date.
    """
    organize(source, dest, remove_source)
