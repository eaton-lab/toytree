#!/usr/bin/env python

"""
Users: Install with conda:
    conda install toytree -c conda-forge

Developers: Install with git + pip
    conda install toytree -c conda-forge
    git clone https://github.com/eaton-lab/toytree
    cd toytree/
    pip install -e . --no-deps
"""

import re
from pathlib import Path
from setuptools import setup, find_packages

DIR = Path(__file__).parent
LONG_DESC = (DIR / "README.md").read_text()
INIT_DATA = (DIR / "toytree/__init__.py").read_text()
VERSION = re.search(
    r"^__version__ = ['\"]([^'\"]*)['\"]",
    INIT_DATA,
    re.M,
).group(1)

# run setup
setup(
    name="toytree",
    version=VERSION,
    url="https://github.com/eaton-lab/toytree",
    author="Deren Eaton",
    author_email="de2356@columbia.edu",
    description="minimalist tree plotting using toyplot",
    long_description=LONG_DESC,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    # packages=find_packages(),
    install_requires=[
        "toyplot",
        "numpy",
        "scipy",
        "pandas",
        "loguru",
        "requests",
        # "ghostscript"
        # "pillow"
    ],
    entry_points={},
    license='GPLv3',
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
)
