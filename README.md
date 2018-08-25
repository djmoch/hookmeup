# Hook Me Up

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
