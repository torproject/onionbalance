#!/bin/bash
set -ex

pytest --cov-report=term-missing --cov=onionbalance --ignore=test/functional/
pylint onionbalance --disable=R,C,W --ignore=test/functional/
flake8 onionbalance