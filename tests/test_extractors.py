from pathlib import Path

import pytest

from image_date_organizer.extractors import ExifImageExtractor


@pytest.fixture
def jpeg_img(data_dir):
    return data_dir / Path("gibraltar.jpg")


def test_exif_extractor(jpeg_img):
    date = ExifImageExtractor().extract(jpeg_img)
    assert date.year == 2018
    assert date.month == 8
    assert date.day == 17
