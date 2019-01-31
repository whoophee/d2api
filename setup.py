#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Setup script"""

import re

from setuptools import setup

AUTHOR = "Raghav Sairam"
EMAIL = "raghavsairamn@gmail.com"

NAME = 'd2api'
URL = "https://github.com/whoophee/d2api"
DATE = "25/10/2018"
LICENSE = "GPL-3.0"
VERSION = '0.1.0'
DESCR = "Dota 2 API wrapper and parser for Python 3"

setup(
    name = NAME,
    version = VERSION,
    author = AUTHOR,
    author_email = EMAIL,
    url = URL,
    description = DESCR,
    license = LICENSE,
    keywords = "dota2 dota api d2api parser",
    packages = ['d2api', 'd2api.src', 'd2api.ref'],
    package_data = {'d2api.ref': ['abilities.json',
                                   'heroes.json',
                                   'items.json',
                                   'meta.json']},
    install_requires = ['requests'],
    classifiers=[
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ]
)
