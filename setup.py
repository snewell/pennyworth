#!/usr/bin/python3

from setuptools import setup, find_packages

with open('README.rst') as f:
    long_description = f.read()

setup(
    name="pennyworth",
    version="0.1.0",
    package_dir={
        "": "lib"
    },
    packages=find_packages("lib"),

    install_requires=[
        'jenkinsapi==0.3.6'
    ],

    entry_points={
        "console_scripts": [
            "pennyworth = pennyworth.driver:main"
        ],
        'pennyworth.commands': [
            'list-jobs = pennyworth.list_jobs:_LIST_JOBS_COMMAND'
        ],
    },

    author="Stephen Newell",
    description="Manage Jenkins build configurations",
    long_description=long_description,
    long_description_content_type='text/x-rst',
    license="BSD-2",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Topic :: Software Development",
        "Topic :: Utilities"
    ]
)
