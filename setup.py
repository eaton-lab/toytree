#!/usr/bin/env python

"""
Uesrs: Install with conda:
    conda install toytree -c conda-forge

Developers: Install with git + pip
    conda install toytree -c conda-forge
    git clone https://github.com/eaton-lab/toytree
    cd toytree/
    pip install -e . --no-deps
"""

import re
from setuptools import setup, find_packages


# get version from __init__.py
INITFILE = "toytree/__init__.py"
CUR_VERSION = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                    open(INITFILE, "r").read(),
                    re.M).group(1)

# run setup
setup(
    name="toytree",
    version=CUR_VERSION,
    url="https://github.com/eaton-lab/toytree",
    author="Deren Eaton",
    author_email="de2356@columbia.edu",
    description="minimalist tree plotting using toyplot",
    long_description=open('README.md').read(),
    long_description_content_type='text/x-rst',
    packages=find_packages(),
    # packages=find_packages(),
    install_requires=[
        "toyplot",
        "numpy",
        "scipy",
        "pandas",
        "loguru",
        "requests",
        "future",
    ],
    entry_points={},
    license='GPLv3',
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
)
