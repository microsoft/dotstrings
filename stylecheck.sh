#!/bin/bash

pushd "${VIRTUAL_ENV}" > /dev/null

python -m black -l 100 dotstrings/*.py

python -m pylint --rcfile=pylintrc dotstrings
python -m mypy --ignore-missing-imports dotstrings/

python -m pylint --rcfile=pylintrc tests
python -m mypy --ignore-missing-imports tests/

popd > /dev/null

