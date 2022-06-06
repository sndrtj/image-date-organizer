import re
from pathlib import Path

import pytest

from image_date_organizer.extractors import ExifImageExtractor, RegexExtractor


@pytest.fixture
def jpeg_img(data_dir):
    return data_dir / Path("gibraltar.jpg")


@pytest.fixture
def weevil_img(data_dir):
    return data_dir / Path("20210613_164236.jpg")


def test_exif_extractor(jpeg_img):
    date = ExifImageExtractor().extract(jpeg_img)
    assert date.year == 2018
    assert date.month == 8
    assert date.day == 17


def test_regex_extractor(weevil_img):
    extractor = RegexExtractor(re.compile(r"(\d{8}_\d{6})"), "YYYYMMDD_HHmmss")
    date = extractor.extract(weevil_img)
    assert date.year == 2021
    assert date.month == 6
    assert date.day == 13
