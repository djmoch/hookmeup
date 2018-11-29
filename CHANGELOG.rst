Changelog
=========

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog`_ , and this project adheres to
`Semantic Versioning`_.

Unreleased_
-----------

Added
~~~~~

- ``CHANGELOG.rst``

- Contributing and Releases sections added to README

Changed
~~~~~~~

- References to Github repo changed to point to git.danielmoch.com
  (Github is now a mirror only)

v1.0.3_ – 2018-10-31
--------------------

Added
~~~~~

- Dynamic executable name detection

v1.0.2_ – 2018-10-31
--------------------

Added
~~~~~

- PGP signatures to live alongside source and wheel artifacts on PyPI

v1.0.1_ – 2018-09-17
--------------------

Changed
~~~~~~~

- PyPI documentation and metadata

v1.0.0_ – 2018-09-16
--------------------

Added
~~~~~

- 1.0 maturity level for CLI API

v0.2.0_ – 2018-09-01
--------------------

Added
~~~~~

- Support for all versions of Python 3

- CI tests back to Python 3.4

v0.1.2_ – 2018-08-30
--------------------

Added
~~~~~

- Support for Windows (including CI)

Changed
~~~~~~~

- Fix Pipenv checking so that ``pipenv sync`` is run if either
  ``Pipfile`` or ``Pipfile.lock`` has changed

v0.1.1_ – 2018-08-29
--------------------

Changed
~~~~~~~

- Treat ``branch_checkout`` parameter in ``post-checkout`` parser as an
  integer instead of a string

v0.1.0 - 2018-08-25
-------------------

Added
~~~~~

- Initial beta release

.. _Keep a Changelog: https://keepachangelog.com/en/1.0.0/
.. _Semantic Versioning: https://semver.org/spec/v2.0.0.html
.. _Unreleased: https://git.danielmoch.com/hookmeup.git/diff/?id=master&id2=v1.0.3
.. _v1.0.3: https://git.danielmoch.com/hookmeup.git/diff/?id=v1.0.3&id2=v1.0.2
.. _v1.0.2: https://git.danielmoch.com/hookmeup.git/diff/?id=v1.0.2&id2=v1.0.1
.. _v1.0.1: https://git.danielmoch.com/hookmeup.git/diff/?id=v1.0.1&id2=v1.0.0
.. _v1.0.0: https://git.danielmoch.com/hookmeup.git/diff/?id=v1.0.0&id2=v0.2.0
.. _v0.2.0: https://git.danielmoch.com/hookmeup.git/diff/?id=v0.2.0&id2=v0.1.2
.. _v0.1.2: https://git.danielmoch.com/hookmeup.git/diff/?id=v0.1.2&id2=v0.1.1
.. _v0.1.1: https://git.danielmoch.com/hookmeup.git/diff/?id=v0.1.1&id2=v0.1.0
