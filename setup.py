#!/usr/bin/env python

from setuptools import setup, find_packages
import re

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
    long_description=open('README.rst').read(),
    packages=find_packages(),
    install_requires=[
        "toyplot>=0.17.0",
        "numpy>=1.8.0",
        "future",
        "requests",
    ],
    entry_points={},
    license='GPL',
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
)