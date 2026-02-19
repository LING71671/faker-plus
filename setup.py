#!/usr/bin/env python

from pathlib import Path

from setuptools import find_packages, setup

here = Path(__file__).resolve().parent
README = (here / "README.md").read_text(encoding="utf-8")
VERSION = (here / "VERSION").read_text(encoding="utf-8").strip()

excluded_packages = ["docs", "tests", "tests.*"]


# this module can be zip-safe if the zipimporter implements iter_modules or if
# pkgutil.iter_importer_modules has registered a dispatch for the zipimporter.
try:
    import pkgutil
    import zipimport

    zip_safe = (
        hasattr(zipimport.zipimporter, "iter_modules")
        or zipimport.zipimporter in pkgutil.iter_importer_modules.registry.keys()
    )
except AttributeError:
    zip_safe = False

setup(
    name="faker-plus",
    version=VERSION,
    description="Faker is a Python package that generates fake data for you.",
    long_description=README,
    long_description_content_type="text/markdown",
    entry_points={
        "console_scripts": ["faker=faker.cli:execute_from_command_line"],
        "pytest11": ["faker = faker.contrib.pytest.plugin"],
    },
    classifiers=[
        # See https://pypi.org/pypi?%3Aaction=list_classifiers
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Testing",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ],
    keywords="faker fixtures data test mock generator",
    author="LING71671",
    author_email="ling71671@gmail.com",
    url="https://github.com/LING71671/faker-plus",
    project_urls={
        "Bug Tracker": "https://github.com/LING71671/faker-plus/issues",
        "Changes": "https://github.com/LING71671/faker-plus/blob/master/CHANGELOG.md",
        "Documentation": "http://faker.rtfd.org/",
        "Source Code": "https://github.com/LING71671/faker-plus",
    },
    license="MIT License",
    packages=find_packages(exclude=excluded_packages),
    package_data={
        "faker": ["py.typed", "proxy.pyi"],
    },
    platforms=["any"],
    zip_safe=zip_safe,
    install_requires=['tzdata; platform_system=="Windows"'],
    extras_require={
        "tzdata": ["tzdata"],
    },
    python_requires=">=3.10",
)
