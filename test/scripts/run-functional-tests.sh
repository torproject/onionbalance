#!/bin/bash
set -ex

[[ $TEST =~ functional_(.*) ]]
version="${BASH_REMATCH[1]}"
source test/scripts/install-chutney-v3.sh
pwd
pytest --cov-report=term-missing --cov=onionbalance test/functional/$version/
pylint --disable=R,C,W onionbalance
flake8 onionbalance
