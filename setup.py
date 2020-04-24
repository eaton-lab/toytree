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
    long_description_content_type='text/x-rst',
    packages=find_packages(),
    install_requires=[
        "toyplot",
        "numpy",
        "requests",
        "future",
    ],
    entry_points={},
    license='GPL',
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
)
