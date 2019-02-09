from setuptools import setup, find_packages

setup(
    name="image_date_organizer",
    description="Import and organize images by EXIF/XMP date.",
    author="Sander Bollen",
    version="0.1.0-dev",
    author_email="sander@sndrtj.eu",
    license="BSD-3-clause",
    packages=find_packages(),
    python_requires=">=3.5",
    install_requires=[
        "click>=7.0",
        "pillow>=5.4.1",
        "pendulum>=2.0.4",
        "python-magic>=0.4.15"
    ],
    entry_points={
        "console_scripts": [
            "image-date-organizer = image_date_organizer.cli:main"
        ]
    }
)
