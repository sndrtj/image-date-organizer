"""
test_organize.py
~~~~~~~~~~~~~~~~

:copyright: (c) 2019 Sander Bollen
:license: BSD-3-clause
"""
from datetime import datetime
from pathlib import Path

import pytest

from image_date_organizer.organize import create_date_path, is_image


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
