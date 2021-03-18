# boa - backup over anything
[![Tests](https://github.com/Kitesoft-dev/boa/actions/workflows/tests.yml/badge.svg)](https://github.com/Kitesoft-dev/boa/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/Kitesoft-dev/boa/branch/main/graph/badge.svg?token=F00J7GP6GQ)](https://codecov.io/gh/Kitesoft-dev/boa)

## Installation

## Usage
### Source
To use *boa* inside your python project, you just need to import it.

This is an example of usage:
```python
import boa

boa.backup("path/to/source", "path/to/dest")

# optional test
fin = open("path/to/source")
fout = open("path/to/dest")
assert fin.read() == fout.read()
```
That's it.

## Development
In order to improve *boa*, you need to follow these simple steps:
- install dev requirements running `pip install -r requirements/dev.txt`;
- run `pre-commit install` to install project's git hooks;
- run `tox` to check if your code pass tests and linters' checks;
- push your changes.