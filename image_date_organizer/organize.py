"""
image_date_organizer.organize
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2019 Sander Bollen
:license: BSD-3-clause
"""
from datetime import datetime
from pathlib import Path
import shutil
import logging

import magic
import pendulum
from PIL import Image
from PIL.ExifTags import TAGS

from .utils import sha256_file

logger = logging.getLogger("image-date-organizer")


_exif_date_field = next(k for k, v in TAGS.items() if v == "DateTime")


def is_image(path: Path):
    mimetype = magic.from_file(str(path), mime=True)
    return mimetype.split("/")[0] == "image"


def verify_copy(source: Path, destination: Path):
    """
    Copy a file, verifying that the copied file's contents are identical
    to the source contents.

    Will attempt to copy metadata as well, with the caveats listed in:
    https://docs.python.org/3.7/library/shutil.html#shutil.copy2

    In case the contents do not match, we will attempt to remove the
    destination if it is a file, after which a ValueError is thrown.

    :raises: ValueError in case contents do not match
    :raises: ValueError in case source is not a file
    :raises: ValueError in case destination is a directory.
    :raises: OSError in case file's can't be written.
    """
    if not source.is_file():
        raise ValueError("Source must be a file")
    if destination.is_dir():
        raise ValueError("Destination may not be a directory")
    source_sha256 = sha256_file(source)
    copied = Path(shutil.copy2(source, destination))
    dest_sha256 = sha256_file(copied)
    if source_sha256 != dest_sha256:
        if copied.is_file():
            copied.unlink()
        raise ValueError("Source' and destination's contents did not match!")


def get_date_from_image(path: Path) -> datetime:
    image = Image.open(path)
    if "exif" in image.info:
        exif_data = image._getexif()
        if _exif_date_field in exif_data:
            return pendulum.parse(exif_data[_exif_date_field])
        logger.warning(
            "Could not determine creation date for {0}, "
            "defaulting to mtime".format(str(path))
        )
        mtime = path.stat().st_mtime
        return pendulum.from_timestamp(mtime)
    else:
        logger.warning(
            "Could not determine creation date for {0}, "
            "defaulting to mtime".format(str(path))
        )
        mtime = path.stat().st_mtime
        return pendulum.from_timestamp(mtime)


def create_date_path(root: Path, date: datetime) -> Path:
    """Create path form a root path and a date."""
    return (root / Path(str(date.year)) / Path(str(date.month)) /
            Path(str(date.day)))


def organize_file(source: Path, destination: Path,
                  remove_source: bool = False):
    """Organize a single file."""
    if not is_image(source):
        logger.warning("{0} is not an image, skipping".format(str(source)))
        return  # skipping since is not an image
    date = get_date_from_image(source)
    dest_dir = create_date_path(destination, date)
    dest_dir.mkdir(parents=True, exist_ok=True)  # ensure dir exists
    dest_path = dest_dir / source.name
    logger.debug("Determined destination path as {0}".format(str(dest_path)))
    if dest_path.exists():
        logger.warning("{0} already exists on destination, skipping".format(
            source.name)
        )
        return  # skipping, since it already exists.
    logger.info("Copying {0} to {1}".format(str(source), str(dest_path)))
    try:
        verify_copy(source, dest_path)
    except ValueError:
        logger.exception("Failed to copy {0} to {1}".format(
            str(source), str(dest_path))
        )
        raise
    if remove_source and source.is_file():
        logger.info("Removing {0}".format(str(source)))
        source.unlink()  # removing source.


def organize_dir(source: Path, destination: Path, remove_source: bool = False):
    """
    Recursively organize a directory.

    :raises: RuntimeError when trying to process extremely deep directory tree.
    """
    for item in source.iterdir():
        if item.is_file():
            organize_file(item, destination, remove_source)
        elif item.is_dir():
            # a little recursion
            organize_dir(item, destination, remove_source)
        else:
            # skipping due to don't know how to handle
            continue

    if remove_source:
        try:
            source.rmdir()
        except OSError as error:
            if str(error).startswith("[Errno 39]"):
                # means directory is not empty.
                # should warn that source is unremovable.
                pass
            else:
                raise


def organize(source: Path, destination: Path, remove_source: bool = False):
    """Main organizer"""
    if source.is_file():
        logger.debug("{0} is a file".format(str(source)))
        organize_file(source, destination, remove_source)
    elif source.is_dir():
        logger.debug("{0} is a directory".format(str(source)))
        organize_dir(source, destination, remove_source)
    else:
        raise NotImplementedError
