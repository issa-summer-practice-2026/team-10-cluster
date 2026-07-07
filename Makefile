# Convenience wrapper around scripts/dev.py (Unix). Override the interpreter
# with `make PY=python setup` if `python3` is not your Python 3.11+ binary.
PY ?= python3

.PHONY: setup dev build run test lint help

help:
	@echo "targets: setup | dev | build | run | test | lint"

setup:
	$(PY) scripts/dev.py setup

dev:
	$(PY) scripts/dev.py dev

build:
	$(PY) scripts/dev.py build

run:
	$(PY) scripts/dev.py run

test:
	$(PY) scripts/dev.py test

lint:
	$(PY) scripts/dev.py lint
