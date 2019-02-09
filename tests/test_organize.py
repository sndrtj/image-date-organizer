"""
test_organize.py
~~~~~~~~~~~~~~~~

:copyright: (c) 2019 Sander Bollen
:license: BSD-3-clause
"""
from pathlib import Path
from datetime import datetime


from image_date_organizer.organize import create_date_path


def test_create_date_path(data_dir):
    now = datetime.utcnow()
    now_part = Path(str(now.year)) / Path(str(now.month)) / Path(str(now.day))
    expected = data_dir / now_part
    assert create_date_path(data_dir, now) == expected
