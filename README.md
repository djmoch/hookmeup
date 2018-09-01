# Hook Me Up

![GitHub](https://img.shields.io/github/license/djmoch/hookmeup.svg)
[![Travis (.com)](https://img.shields.io/travis/com/djmoch/hookmeup.svg?logo=travis)](https://travis-ci.com/djmoch/hookmeup)
[![AppVeyor](https://img.shields.io/appveyor/ci/djmoch/hookmeup.svg?logo=appveyor)](https://ci.appveyor.com/project/djmoch/hookmeup)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/hookmeup.svg)
[![PyPI](https://img.shields.io/pypi/v/hookmeup.svg)](https://pypi.org/project/hookmeup/)
[![Coverage Status](https://coveralls.io/repos/github/djmoch/hookmeup/badge.svg?branch=master)](https://coveralls.io/github/djmoch/hookmeup?branch=master)

A Git hook to automate your Pipenv and Django workflows

## Requires

- Python 3.5 or newer

## Features

- Fires whenever you switch branches with `git checkout`
- Cleans and Syncs your Pipenv if there are changes to `Pipfile`
- Migrates your Django DB to it's current working state, applying and
  unapplying migrations as necessary

The hook detects if Pipenv and/or Django are in use in the current repo,
so you don't need to be using both to take advantage of Hookmeup.

## Usage

```
$ pip install hookmeup
$ cd $YOUR_PROJECT
$ hookmeup install
```

More details are available by running `hookmeup --help`.

## Acknowledgments

hookmeup is inspired by Tim Pope's
[hookup](https://github.com/tpope/hookup) utility for Ruby/Rails (and
hence so is the name).
