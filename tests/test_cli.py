"""
test_cli.py
~~~~~~~~~~~

:copyright: (c) 2019 Sander Bollen
:license: BSD-3-clause
"""
from pathlib import Path

from image_date_organizer.cli import path_callback


def test_path_callback():
    assert path_callback(None, None, "test") == Path("test")
