"""
test_utils.py
~~~~~~~~~~~~~

:copyright: (c) 2019 Sander Bollen
:license: BSD-3-clause
"""
from pathlib import Path
import pytest

from image_date_organizer.utils import sha256_file


def test_sha256_file(rand_file):
    assert sha256_file(rand_file) == (
        "9d55a64228d8d47d2b944b5e76b298bcc65b1919956231fc34fb8c87350c2de1"
    )


def test_sha256_file_not_found():
    with pytest.raises(FileNotFoundError):
        sha256_file(Path("does_not_exists__by_a_long_shot"))


def test_sha256_file_invalid_chunksize(rand_file):
    with pytest.raises(ValueError):
        sha256_file(rand_file, -1)
