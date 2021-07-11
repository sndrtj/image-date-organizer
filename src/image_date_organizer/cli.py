"""
image_date_organizer.cli
~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2019-2021 Sander Bollen
:license: BSD-3-clause
"""
import pathlib
import click
from typing import Any

from .organize import Organizer, DEFAULT_IMAGE_EXTRACTORS, DEFAULT_VIDEO_EXTRACTORS
from .utils import get_package_version

from loguru import logger


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
    "--remove-source / --no-remove-source",
    help="Enable to remove the source files after import was completed.",
    default=False,
)
@click.option("--dry-run / --no-dry-run", help="Perform a dry run.", default=False)
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
    dry_run: bool,
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
    logger.info(f"Organizing {source} into destination {dest}")
    organizer = Organizer(
        image_extractors=DEFAULT_IMAGE_EXTRACTORS,
        video_extractors=DEFAULT_VIDEO_EXTRACTORS,
        remove_source=remove_source,
        dry_run=dry_run,
    )
    organizer.organize(source, dest)
