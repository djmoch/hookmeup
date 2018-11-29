# Hook Me Up

[![PyPI - License](https://img.shields.io/pypi/l/hookmeup.svg)](https://pypi.org/project/hookmeup/)
[![Travis (.com)](https://img.shields.io/travis/com/djmoch/hookmeup.svg?logo=travis)](https://travis-ci.com/djmoch/hookmeup)
[![AppVeyor](https://img.shields.io/appveyor/ci/djmoch/hookmeup.svg?logo=appveyor)](https://ci.appveyor.com/project/djmoch/hookmeup)
[![PyPI](https://img.shields.io/pypi/v/hookmeup.svg)](https://pypi.org/project/hookmeup/)
[![Coverage Status](https://coveralls.io/repos/github/djmoch/hookmeup/badge.svg?branch=master)](https://coveralls.io/github/djmoch/hookmeup?branch=master)

A Git hook to automate your Pipenv and Django workflows

## Requirements

- Python 2.7+

## Features

- Fires whenever you switch branches with `git checkout`, or whenever
  you run `git pull`, or basically any time Git checks files out into
  your worktree
- Cleans and Syncs your Pipenv if there are changes to `Pipfile` or
  `Pipfile.lock`
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

## Contributing

Pull requests are welcome, preferably via emailed output of `git
request-pull` sent to the maintainer (see
[here](https://www.git-scm.com/docs/git-request-pull) for more
information).  Bug reports should also be directed to the maintainer via
email.

## Releases

Release tags will always be signed with the maintainer's [PGP
key](https://www.danielmoch.com/static/gpg.asc) (also available on any
public
[keyserver](https://pgp.mit.edu/pks/lookup?op=get&search=0x323C9F1784BDDD43)).
PGP-signed versions of release tarballs and pre-built
[wheel](https://pythonwheels.com/) packages are available on
[PyPI](https://pypi.org/project/hookmeup/), with the signature files
living alongside the corresponding artifact (simply append an `.asc`
extension). Because the maintainers of PyPI do not consider PGP
signatures to be a user-facing feature, the extension must be added
manually in your browser's URL bar in order to download the signature
files.

## Acknowledgments

hookmeup is inspired by Tim Pope's
[hookup](https://github.com/tpope/hookup) utility for Ruby/Rails (and
hence so is the name).
