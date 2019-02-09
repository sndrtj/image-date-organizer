"""
image_date_organizer.utils
~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2019 Sander Bollen
:license: BSD-3-clause
"""
import hashlib
from pathlib import Path
import pkg_resources


def get_package_version():
    return pkg_resources.get_distribution("image_date_organizer").version


def sha256_file(path: Path, chunksize: int = 4*1024*1024) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            data = handle.read(chunksize)
            if not data:
                break
            hasher.update(data)
    return hasher.hexdigest()
