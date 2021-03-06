"""
image_date_organizer.cli
~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2019 Sander Bollen
:license: BSD-3-clause
"""
import pathlib
import click
import logging
from typing import Any

from .organize import organize
from .utils import get_package_version

logger = logging.getLogger("image-date-organizer")


def path_callback(
    ctx: click.Context, param: click.Parameter, value: Any
) -> pathlib.Path:
    """Click fallback function for generating pathlib.Path instances"""
    return pathlib.Path(value)


@click.command(name="image_date_organizer")
@click.version_option(get_package_version())
@click.argument("source", type=click.Path(readable=True), callback=path_callback)
@click.option(
    "-d",
    "--dest",
    type=click.Path(dir_okay=True, file_okay=False, writable=True),
    required=True,
    callback=path_callback,
    help="Destination directory",
)
@click.option(
    "--remove-source",
    is_flag=True,
    help="Enable to remove the source files after import was " "completed.",
)
@click.option(
    "-l",
    "--log-level",
    type=click.Choice(["ERROR", "WARNING", "INFO", "DEBUG"]),
    default="INFO",
)
def main(
    source: pathlib.Path,
    dest: pathlib.Path,
    remove_source: bool,
    log_level: str = "INFO",
):
    """
    Import images and mp4 videos from source and organize them into destination by date.

    Source may be either a single file or a directory. In case of the latter,
    the source directory will be searched recursively for image and mp4 files.

    Images will be organized first by year, then by month, and lastly by day.

    Dates will be taken from EXIF or XMP metadata fields, if available.
    If no such metadata fields are available, we will fall back to mtime as
    the source of date.

    This tool depends on exiftool being installed on your system.
    See https://exiftool.org/.
    """
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=log_level
    )
    logger.info("Organizing {0} into destination {1}".format(str(source), str(dest)))
    organize(source, dest, remove_source)
