"""
image_date_organizer.extractors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2019-2022 Sander Bollen
:license: BSD-3-clause
"""
import abc
import datetime
import pathlib
import re
import subprocess
from typing import Optional, cast

import pendulum
from loguru import logger
from PIL import Image
from PIL.ExifTags import TAGS

EXIF_DATE_FIELD = next(k for k, v in TAGS.items() if v == "DateTime")


class Extractor(abc.ABC):
    def __init__(self, ignore_errors: bool = False):
        """Initialize extractor

        :param ignore_errors: Set to True if you want to ignore errors for this
            extractor. We will still log the error, but the application will progress if
            this is set to true. Defaults to False.
        """
        self.ignore_errors = ignore_errors

    @abc.abstractmethod
    def extract(self, path: pathlib.Path) -> Optional[datetime.date]:
        """Extract date from an image or video file.

        Must be implemented in subclasses.

        :param path: Concrete path to the image or video.
        :return: Date when we can extract the date, None otherwise
        """
        ...


class ExifImageExtractor(Extractor):
    """
    Extract the date using the EXIF date tag.
    """

    def extract(self, path: pathlib.Path) -> Optional[datetime.date]:
        image = Image.open(path)
        date: Optional[datetime.date] = None
        if "exif" in image.info:
            exif_data = image._getexif()
            if EXIF_DATE_FIELD in exif_data:
                date = cast(
                    pendulum.DateTime, pendulum.parse(exif_data[EXIF_DATE_FIELD])
                ).date()
        return date


class RegexExtractor(Extractor):
    """
    Extract the date using a regex pattern in the filename.
    """

    def __init__(self, pattern: re.Pattern, date_fmt: str, **kwargs):
        """Initialize RegexExtractor

        :param pattern: Regex pattern with at least one capture group. The first
            capture group should correspond to the date(time) part of the filename.
        :param date_fmt: Format-specifier to convert the extracted string to a
            pendulum datetime. Should be in pendulum format. Example 'YYYY-MM-DD'.
        :param kwargs: Additional keyword arguments passed to superclass

        """
        super().__init__(**kwargs)
        if pattern.groups < 1:
            raise ValueError("Supplied pattern does not contain a capture group")
        self.pattern = pattern
        self.date_fmt = date_fmt

    def extract(self, path: pathlib.Path) -> Optional[datetime.date]:
        """Extract date from path using regex.

        :param path: Path to image or video.
        :return: Extracted date when there is a match, None otherwise.
        :raises: ValueError when date format specifier does not match extracted
            capture group field.
        """
        match = self.pattern.match(path.name)

        if match is None:
            return None

        try:
            dt = pendulum.from_format(match.group(1), self.date_fmt)
        except ValueError:
            logger.exception(
                f"Could not extract date of {path.name} using pattern {self.date_fmt}"
            )
            if self.ignore_errors:
                return None
            raise

        return dt.date()


class ExifToolExtractor(Extractor):
    """Extract dates using exiftool.

    This is especially relevant for videos, as PIL does not parse videos, we
    have to use another approach here. Exiftool must be on the PATH for this
    extractor to work.
    """

    def extract(self, path: pathlib.Path) -> Optional[datetime.date]:
        """Extract the date

        :param path: Path of image or video
        :return: Date when it is possible to extract so, None when date is not found
            in exiftool output.
        :raises: CalledProcessError when exiftool gives a non-zero exit code
        :raises: FileNotFoundError in case exiftool was not found on the PATH
        """
        try:
            proc_return = subprocess.run(
                ["exiftool", path], capture_output=True, text=True, check=True
            )
        except subprocess.CalledProcessError:
            logger.exception(f"Exiftool had a non-zero exit code for file {path}")
            if self.ignore_errors:
                return None
            raise
        except FileNotFoundError:
            logger.exception("Exiftool was not found on the PATH.")
            if self.ignore_errors:
                return None
            raise

        date: Optional[datetime.date] = None
        for line in proc_return.stdout.splitlines():
            if line.startswith("Create Date"):
                _, _, date_field = line.partition(":")
                try:
                    date = cast(
                        pendulum.DateTime, pendulum.parse(date_field.strip())
                    ).date()
                except ValueError:
                    logger.warning(
                        f"Could not determine exif-provided date for {path}. "
                        f"{date_field} is not a valid date-time."
                    )

        return date


class MTimeExtractor(Extractor):
    """Simple extractor based on mtime"""

    def extract(self, path: pathlib.Path) -> Optional[datetime.date]:
        """Extract date

        :param path: Path to file
        :return: Date of modified time of the file.
        """
        dt = pendulum.from_timestamp(path.stat().st_mtime)
        return dt.date()
