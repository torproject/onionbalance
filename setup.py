# -*- coding: utf-8 -*-

"""setup.py: setuptools control."""

import io
import os

from setuptools import setup
from onionbalance import __version__

# Read version and other info from package's __init.py file
module_info = {}
init_path = os.path.join(os.path.dirname(__file__), 'onionbalance',
                         '__init__.py')
with open(init_path) as init_file:
    exec(init_file.read(), module_info)


def read(*names, **kwargs):
    return io.open(
        os.path.join(os.path.dirname(__file__), *names),
        encoding=kwargs.get("encoding", "utf8")
    ).read()

setup(
    name="Onionbalance",
    packages=["onionbalance",
              "onionbalance.hs_v3", "onionbalance.hs_v3.ext", "onionbalance.common",
              "onionbalance.config_generator"],
    entry_points={
        "console_scripts": [
            'onionbalance = onionbalance.manager:main',
            'onionbalance-config = onionbalance.config_generator.config_generator:main',
        ]},
    description="Onionbalance provides load-balancing and redundancy for Tor "
                "hidden services by distributing requests to multiple backend "
                "Tor instances.",
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    author=module_info.get('__author__'),
    author_email=module_info.get('__contact__'),
    url=module_info.get('__url__'),
    license=module_info.get('__license__'),
    keywords='tor',
    python_requires='>=3.6',
    install_requires=[
        'setuptools',
        'stem>=1.8',
        'PyYAML>=4.2b1',
        'pycryptodomex',
        'setproctitle',
        'cryptography>=2.5',
    ],
    tests_require=['pytest-mock', 'pytest', 'mock', 'pexpect', 'pylint', 'flake8', 'coveralls'],
    package_data={'onionbalance.config_generator': ['data/*']},
    include_package_data=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
    ],
    version=__version__,
)
