#!/bin/bash

pushd "${VIRTUAL_ENV}/.." > /dev/null

python -m black -l 100 dotstrings/*.py

python -m pylint --rcfile=pylintrc dotstrings tests
python -m mypy --ignore-missing-imports dotstrings/ tests/

popd > /dev/null

