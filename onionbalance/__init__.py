# -*- coding: utf-8 -*-

__author__ = "Silvio Rhatto, George Kadianakis, Donncha O'Cearbhaill"
__contact__ = "rhatto@torproject.org"
__url__ = "https://gitlab.torproject.org/tpo/onion-services/onionbalance/"
__license__ = "GPL"

from onionbalance._version import get_versions
__version__ = get_versions()['version']
del get_versions
