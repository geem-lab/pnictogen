#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import setup

version_file = open(os.path.join(".", "VERSION"))
version = version_file.read().strip()
download_url = \
   'https://github.com/dudektria/pnictogen/archive/{:s}.tar.gz'.format(version)

doclines = """pnictogen: input generation for computational chemistry packages

pnictogen is a Python library that generates input files for computational
chemistry packages.
""".split("\n")

# Chosen from http://www.python.org/pypi?:action=list_classifiers
classifiers = """Development Status :: 3 - Alpha
Environment :: Console
Intended Audience :: Science/Research
Intended Audience :: Education
Intended Audience :: Developers
License :: OSI Approved :: MIT License
Natural Language :: English
Operating System :: OS Independent
Programming Language :: Python
Programming Language :: Python :: 3
Topic :: Scientific/Engineering :: Chemistry
Topic :: Education
Topic :: Software Development :: Libraries :: Python Modules"""

keywords = [
    'science',
    'research',
    'chemistry',
]

# The list of packages to be installed.
packages = [
    'pnictogen',
]

install_requires = [
    'nose',
    'parse',
    'pyyaml',
    'jinja2',
    'cinfony',
    # 'openbabel',
]

data_files = [('.', ['examples/*'])]

setup(
    name='pnictogen',
    version=version,
    url='https://github.com/dudektria/pnictogen',
    download_url=download_url,
    author='Felipe Silveira de Souza Schneider',
    author_email='schneider.felipe@posgrad.ufsc.br',
    license='MIT',
    description=doclines[0],
    long_description="\n".join(doclines[2:]),
    classifiers=classifiers.split("\n"),
    packages=packages,
    keywords=keywords,
    install_requires=install_requires,
    data_files=data_files,
    test_suite='nose.collector',
    entry_points={
        'console_scripts': [
            'pnictogen = pnictogen:main',
        ],
    },
)
