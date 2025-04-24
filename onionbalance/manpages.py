#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Generates Onionbalance manpages from CLI usage and templates.
#
# Copyright (C) 2025 The Tor Project, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License,
# or any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Dependencies
import os
import datetime
import re
import sys

# Expand the search path to include the parent folder
# Useful when invoking this script in local Onionbalance installations
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from onionbalance.common.argparser import get_common_argparser as onionbalance_parser # noqa: E402
from onionbalance.config_generator.config_generator import parse_cmd_args as onionbalance_config_parser # noqa: E402

basepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir) + os.sep
manpages = {
    'onionbalance': {
        'parser': onionbalance_parser(),
        'template': os.path.join(basepath, 'docs', 'man', 'onionbalance.1.txt.tmpl'),
        'output': os.path.join(basepath, 'docs', 'man', 'onionbalance.1.txt'),
        'config': os.path.join(basepath, 'onionbalance', 'config_generator', 'data', 'config.example.yaml')},

    'onionbalance-config': {
        'parser': onionbalance_config_parser(),
        'template': os.path.join(basepath, 'docs', 'man', 'onionbalance-config.1.txt.tmpl'),
        'output': os.path.join(basepath, 'docs', 'man', 'onionbalance-config.1.txt'),
        'config': os.path.join(basepath, 'onionbalance', 'config_generator', 'data', 'config.example.yaml')}}

def remove_usage_prefix(text):
    """
    Simply removes the "usage: " string prefix from a text.

    :type text : str
    :param text: The input text.

    :rtype: str
    :return: The text without the "usage: string"
    """

    return text.replace('usage: ', '')

def format_as_markdown_verbatim(text):
    """
    Formats a text as a Markdown verbatim block.

    :type text : str
    :param text: The input text.

    :rtype: str
    :return: Formatted text.
    """

    # Some handy regexps
    lines = re.compile('^', re.MULTILINE)
    trailing = re.compile('^ *$', re.MULTILINE)

    return trailing.sub('', lines.sub('    ', text))

def generate():
    """
    Produces the manpage in Markdown format.

    Apply argument parser usage and help into a template.

    """

    # Assume a 80 columm terminal to compile the usage and help texts
    os.environ["COLUMNS"] = "80"

    # Iterate over all manual pages to be built
    for man in manpages:
        # Initialize the command line parser
        parser = manpages[man]['parser']

        # Compile template variables
        usage = remove_usage_prefix(parser.format_usage())
        invocation = remove_usage_prefix(format_as_markdown_verbatim(parser.format_help()))
        date = datetime.datetime.now().strftime('%b %d, %Y')
        config = ''

        if manpages[man]['config'] != '':
            with open(manpages[man]['config'], 'r') as config_file:
                config = format_as_markdown_verbatim(config_file.read())

        with open(manpages[man]['template'], 'r') as template_file:
            with open(manpages[man]['output'], 'w') as output_file:
                contents = template_file.read()

                output_file.write(contents.format(
                    date=date,
                    usage=usage,
                    invocation=invocation,
                    config=config))

# Process from CLI
if __name__ == "__main__":
    generate()
