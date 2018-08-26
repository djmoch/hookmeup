.PHONY: clean clean-test clean-pyc clean-build help lint coverage coverage-html release dist install run debug
.DEFAULT_GOAL := help

define BROWSER_PYSCRIPT
import os, webbrowser, sys

try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"
PIPENV := pipenv run

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +
	pipenv run pip uninstall -y hookmeup

clean-test: ## remove test and coverage artifacts
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache
	rm -fr .tox

lint: ## check style with pylint
	pipenv run pylint --rcfile tests/pylintrc hookmeup tests --disable=parse-error

test: ## run tests quickly with the default Python
	pipenv run python -m pytest

test-all: ## run tests on every Python version with tox
	pipenv run tox

test-install: ## install dependenices from Pipfile (for tox / CI builds)
	pipenv --bare install --dev --skip-lock

coverage: ## check code coverage quickly with the default Python
	pipenv run python -m pytest --cov=hookmeup --cov-config tests/coveragerc
	pipenv run coverage report -m

coverage-html: coverage ## generate an HTML report and open in browser
	pipenv run coverage html
	$(BROWSER) htmlcov/index.html

release: dist ## package and upload a release
	pipenv run flit publish

dist: ## builds source and wheel package
	pipenv run flit build
	ls -l dist

install: ## install the package to the active Python's site-packages
	pipenv run flit install

run: install ## run the package from site-packages
	pipenv run hookmeup

debug: install ## debug the package from site packages
	pipenv run pudb3 `pipenv run which hookmeup`
