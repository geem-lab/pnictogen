#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Package setup script for pnictogen."""

import os.path
from setuptools import setup, find_packages

name = "pnictogen"
this_directory = os.path.abspath(os.path.dirname(__file__))

version_file = open(os.path.join(this_directory, "VERSION"))
version = version_file.read().strip()

url = "https://github.com/dudektria/pnictogen"
download_url = "{:s}/archive/{:s}.tar.gz".format(url, version)

with open(os.path.join(this_directory, "README.rst")) as f:
    long_description = f.read()

setup(
    name=name,
    version=version,
    url=url,
    download_url=download_url,
    author="Felipe S. S. Schneider",
    author_email="schneider.felipe@posgrad.ufsc.br",
    license="MIT",
    description=(
        "A Python library and a command-line tool that creates input "
        "files for computational chemistry packages."
    ),
    long_description=long_description,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Education",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Chemistry",
        "Topic :: Education",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],  # noqa
    keywords=["science", "research", "chemistry"],
    packages=find_packages(exclude=["*test*"]),
    install_requires=["Jinja2>=2.10", "pyrrole"],
    setup_requires=["nose>=1.0"],
    test_suite="nose.collector",
    include_package_data=True,
    entry_points={"console_scripts": ["pnictogen = pnictogen:main"]},
)
