"""
image_date_organizer.organize
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2019-2022 Sander Bollen
:license: BSD-3-clause
"""
import datetime
import pathlib
import re
import shutil
from pathlib import Path
from typing import Optional, Sequence

import magic
from loguru import logger

from .extractors import (
    ExifImageExtractor,
    ExifToolExtractor,
    Extractor,
    MTimeExtractor,
    RegexExtractor,
)
from .utils import sha256_file

DEFAULT_IMAGE_EXTRACTORS = [
    ExifImageExtractor(),
    # e.g. '20200101_120101.jpg'
    RegexExtractor(re.compile(r"(\d{8}_\d{6})"), "YYYYMMDD_HHmmss"),
    # e.g. 'Screenshot_20200101-120101_Maps.jpg'
    RegexExtractor(re.compile(r"Screenshot_(\d{8}-\d{6})_\w.+"), "YYYYMMDD-HHmmss"),
    # e.g. 'IMG-20200101-WA0001.jpg'
    RegexExtractor(re.compile(r"IMG-(\d{8})-WA\d+"), "YYYYMMDD"),
    MTimeExtractor(),
]

DEFAULT_VIDEO_EXTRACTORS = [
    ExifToolExtractor(),
    # e.g. 'VID-20200101-WA0001.mp4'
    RegexExtractor(re.compile(r"VID-(\d{8})-WA\d+"), "YYYYMMDD"),
    MTimeExtractor(),
]


class Organizer:
    """
    The organizer takes care of actually organizing a source directory to a
    destination.

    It uses a sequence of extractors for images and videos to accomplish this task.
    """

    def __init__(
        self,
        image_extractors: Sequence[Extractor] = (),
        video_extractors: Sequence[Extractor] = (),
        dry_run: bool = False,
        remove_source: bool = False,
    ) -> None:
        """Initialize organizer

        :param image_extractors: Ordered sequence of date extractors to use for
            images. Dates are extracted in order. I.e, if the 1st extractor manages
            to extract the date for a particular file, we won't even attempt any of
            the next extractors.
        :param video_extractors: Ordered sequence of date extractors to use for
            videos. Dates are extracted in order. I.e, if the 1st extractor manages
            to extract the date for a particular file, we won't even attempt any
            of the next extractors.
        :param dry_run: Whether to perform a dry run. In a dry run some log messages
            are printed, but we won't actually copy over any files.
        :param remove_source: Whether to remove the source path(s) after copying is
            complete. This parameter is ignored when `dry_run` is set to True.
        """
        self.image_extractors = image_extractors
        self.video_extractors = video_extractors
        self.dry_run = dry_run

        self.remove_source = remove_source if not self.dry_run else False

    def extract_date(self, path: pathlib.Path) -> Optional[datetime.date]:
        """Extract the date of a single file

        :param path: path of file for which we should extract the date.
        :return: Date if file is an image or video and it can be extracted,
            None otherwise.
        """
        if is_image(path):
            return self._extract_image_date(path)
        if is_mp4(path):
            return self._extract_video_date(path)
        logger.warning(f"{path} is not an image or video, skipping...")
        return None

    def _extract_file_date(
        self, path: pathlib.Path, extractors: Sequence[Extractor]
    ) -> Optional[datetime.date]:
        for extractor in extractors:
            logger.debug(f"Attempting extractor {extractor.__class__.__name__}")
            extraction = extractor.extract(path)
            if extraction is not None:
                return extraction

        logger.info("Could not determine date for any extractor.")
        return None

    def _extract_image_date(self, path: pathlib.Path) -> Optional[datetime.date]:
        return self._extract_file_date(path, self.image_extractors)

    def _extract_video_date(self, path: pathlib.Path) -> Optional[datetime.date]:
        return self._extract_file_date(path, self.video_extractors)

    def organize(self, source: Path, destination: Path) -> None:
        """Main organizer"""
        if source.is_file():
            logger.debug(f"{source} is a file")
            self.organize_file(source, destination)
        elif source.is_dir():
            logger.debug(f"{source} is a directory")
            self.organize_dir(source, destination)
        else:
            raise NotImplementedError

    def organize_file(
        self,
        source: Path,
        destination: Path,
    ) -> None:
        """Organize a single file."""
        logger.debug(f"Organizing {source}")
        date = self.extract_date(source)

        if date is None:
            return

        dest_dir = create_date_path(destination, date)

        dest_path = dest_dir / source.name
        logger.debug(f"Determined destination path as {dest_path}")
        dest_dir.mkdir(parents=True, exist_ok=True)  # ensure dir exists
        if dest_path.exists():
            logger.warning(f"{source.name} already exists on destination, skipping")
            return  # skipping, since it already exists.
        logger.info(f"Copying {source} to {dest_path}")

        # Return early if we are doing a dry run.
        if self.dry_run:
            return

        try:
            verify_copy(source, dest_path)
        except ValueError:
            logger.exception(f"Failed to copy {source} to {dest_path}")
            raise

        if self.remove_source and source.is_file():
            logger.info(f"Removing {source}")
            source.unlink()  # removing source.

    def organize_dir(self, source: Path, destination: Path) -> None:
        """
        Recursively organize a directory.

        :raises: RuntimeError when trying to process extremely deep directory tree.
        """
        logger.debug(f"Organizing {source}")
        for item in source.iterdir():
            if item.is_file():
                self.organize_file(item, destination)
            elif item.is_dir():
                # a little recursion
                self.organize_dir(item, destination)
            else:
                # skipping due to don't know how to handle
                continue

        if self.remove_source and not self.dry_run:
            try:
                source.rmdir()
            except OSError as error:
                if str(error).startswith("[Errno 39]"):
                    # means directory is not empty.
                    # should warn that source is unremovable.
                    pass
                else:
                    raise


def is_image(path: Path) -> bool:
    mimetype = magic.from_file(str(path), mime=True)
    return mimetype.split("/")[0] == "image"


def is_mp4(path: Path) -> bool:
    mimetype = magic.from_file(str(path), mime=True)
    return mimetype == "video/mp4"


def verify_copy(source: Path, destination: Path) -> None:
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


def create_date_path(root: Path, date: datetime.date) -> Path:
    """Create path form a root path and a date."""
    return root / Path(str(date.year)) / Path(str(date.month)) / Path(str(date.day))
