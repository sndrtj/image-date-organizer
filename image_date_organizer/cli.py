"""
image_date_organizer.cli
~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2019 Sander Bollen
:license: BSD-3-clause
"""
import click

from .utils import get_package_version


@click.command(name="image_date_organizer")
@click.version_option(get_package_version())
@click.argument("source", type=click.Path(readable=True))
@click.option("-d", "--dest",
              type=click.Path(dir_okay=True, file_okay=False, writable=True),
              required=True,
              help="Destination directory")
def main(source, dest):
    pass
