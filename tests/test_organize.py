"""
test_organize.py
~~~~~~~~~~~~~~~~

:copyright: (c) 2019 Sander Bollen
:license: BSD-3-clause
"""
import pytest
from pathlib import Path
from datetime import datetime


from image_date_organizer.organize import (create_date_path, is_image,
                                           get_date_from_image)


@pytest.fixture
def jpeg_img(data_dir):
    return data_dir / Path("gibraltar.jpg")


def test_create_date_path(data_dir):
    now = datetime.utcnow()
    now_part = Path(str(now.year)) / Path(str(now.month)) / Path(str(now.day))
    expected = data_dir / now_part
    assert create_date_path(data_dir, now) == expected


def test_jpeg_is_image(jpeg_img):
    assert is_image(jpeg_img)


def test_rand_file_is_not_image(rand_file):
    assert not is_image(rand_file)


def test_get_date_from_jpg(jpeg_img):
    date = get_date_from_image(jpeg_img)
    assert date.year == 2018
    assert date.month == 8
    assert date.day == 17
