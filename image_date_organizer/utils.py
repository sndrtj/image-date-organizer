"""
image_date_organizer.utils
~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2019 Sander Bollen
:license: BSD-3-clause
"""
import pkg_resources


def get_package_version():
    return pkg_resources.get_distribution("image_date_organizer").version
