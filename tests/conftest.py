"""
conftest,py
~~~~~~~~~~~

:copyright: (c) 2019 Sander Bollen
:license: BSD-3-clause
"""
from pathlib import Path
import pytest


@pytest.fixture(scope="session")
def data_dir() -> Path:
    return Path(__file__).parent / Path("data")
