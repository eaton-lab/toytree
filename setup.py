#!/usr/bin/env python

from setuptools import setup, find_packages
import glob
import re


def requires():
    """ gets packages from requirements.txt """
    with open('requirements.txt') as infile:
        return infile.read().splitlines()


def dependency_links():
    """ return: the package specifications """
    with open('constraints.txt') as infile:
        return infile.read().splitlines()


## Auto-update ipyrad version from git repo tag
# Fetch version from git tags, and write to version.py.
# Also, when git is not available (PyPi package), use stored version.py.
INITFILE = "toytree/__init__.py"
CUR_VERSION = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                    open(INITFILE, "r").read(),
                    re.M).group(1)

setup(
    name="toytree",
    version=CUR_VERSION,
    url="https://github.com/eaton-lab/toytree",
    author="Deren Eaton",
    author_email="de2356@columbia.edu",
    description="minimalist tree plotting using toyplot",
    long_description=open('README.rst').read(),
    packages=find_packages(),
    install_requires=requires(),
    dependencies=dependency_links(),
    entry_points={},
    license='GPL',
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',         
    ],
)

