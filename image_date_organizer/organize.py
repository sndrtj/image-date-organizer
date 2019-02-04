"""
image_date_organizer.organize
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2019 Sander Bollen
:license: BSD-3-clause
"""
from datetime import datetime
from pathlib import Path

import pendulum
from PIL import Image
from PIL.ExifTags import TAGS


_exif_date_field = next(k for k, v in TAGS.items() if v == "DateTime")


def is_image(path: Path):
    raise NotImplementedError


def get_date_from_image(path: Path) -> datetime:
    image = Image.open(path)
    if "exif" in image.info:
        date_string = image._getexif()[_exif_date_field]
        return pendulum.parse(date_string)
    else:
        raise NotImplementedError
