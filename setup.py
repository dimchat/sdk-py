#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Decentralized Instant Messaging Software Development Kit
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This is a new protocol designed for instant messaging (IM).
    The software provides accounts(user identity recognition) and
    communications between accounts safely by end-to-end encryption.
"""

from setuptools import setup, find_packages

__version__ = '0.5.13'
__author__ = 'Albert Moky'
__contact__ = 'albert.moky@gmail.com'

with open('README.md', 'r') as fh:
    readme = fh.read()

setup(
    name='dimsdk',
    version=__version__,
    url='https://github.com/dimchat/sdk-py',
    license='MIT',
    author=__author__,
    author_email=__contact__,
    description='Decentralized Instant Messaging SDK',
    long_description=readme,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    package_data={
        '': ['res/*.js']
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    install_requires=[
        'dimp>=0.10.16',
        'dkd>=0.10.15',
        'mkm>=0.10.15',

        'pycryptodome',  # 3.7.3
        'base58',  # 1.0.3
        'ecdsa',   # 0.16.1
    ]
)
