# -*- coding: utf-8 -*-

__version__ = "0.1.8"
__author__ = "Donncha O'Cearbhaill"
__contact__ = "donncha@donncha.is"
__url__ = "https://github.com/DonnchaC/onionbalance"
__license__ = "GPL"

from onionbalance._version import get_versions
__version__ = get_versions()['version']
del get_versions
