========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |github-actions| |travis| |appveyor| |requires|
        | |codecov|
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|
.. |docs| image:: https://readthedocs.org/projects/qsiprep_analyses/badge/?style=flat
    :target: https://qsiprep_analyses.readthedocs.io/
    :alt: Documentation Status

.. |travis| image:: https://api.travis-ci.com/GalBenZvi/qsiprep_analyses.svg?branch=main
    :alt: Travis-CI Build Status
    :target: https://travis-ci.com/github/GalBenZvi/qsiprep_analyses

.. |appveyor| image:: https://ci.appveyor.com/api/projects/status/github/GalBenZvi/qsiprep_analyses?branch=main&svg=true
    :alt: AppVeyor Build Status
    :target: https://ci.appveyor.com/project/GalBenZvi/qsiprep_analyses

.. |github-actions| image:: https://github.com/GalBenZvi/qsiprep_analyses/actions/workflows/github-actions.yml/badge.svg
    :alt: GitHub Actions Build Status
    :target: https://github.com/GalBenZvi/qsiprep_analyses/actions

.. |requires| image:: https://requires.io/github/GalBenZvi/qsiprep_analyses/requirements.svg?branch=main
    :alt: Requirements Status
    :target: https://requires.io/github/GalBenZvi/qsiprep_analyses/requirements/?branch=main

.. |codecov| image:: https://codecov.io/gh/GalBenZvi/qsiprep_analyses/branch/main/graphs/badge.svg?branch=main
    :alt: Coverage Status
    :target: https://codecov.io/github/GalBenZvi/qsiprep_analyses

.. |version| image:: https://img.shields.io/pypi/v/connectome-plasticity-project.svg
    :alt: PyPI Package latest release
    :target: https://pypi.org/project/connectome-plasticity-project

.. |wheel| image:: https://img.shields.io/pypi/wheel/connectome-plasticity-project.svg
    :alt: PyPI Wheel
    :target: https://pypi.org/project/connectome-plasticity-project

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/connectome-plasticity-project.svg
    :alt: Supported versions
    :target: https://pypi.org/project/connectome-plasticity-project

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/connectome-plasticity-project.svg
    :alt: Supported implementations
    :target: https://pypi.org/project/connectome-plasticity-project

.. |commits-since| image:: https://img.shields.io/github/commits-since/GalBenZvi/qsiprep_analyses/v0.0.0.svg
    :alt: Commits since latest release
    :target: https://github.com/GalBenZvi/qsiprep_analyses/compare/v0.0.0...main



.. end-badges

A package to process data derived from qsiprep pipeline

* Free software: Apache Software License 2.0

Installation
============

::

    pip install connectome-plasticity-project

You can also install the in-development version with::

    pip install https://github.com/GalBenZvi/qsiprep_analyses/archive/main.zip


Documentation
=============


https://qsiprep_analyses.readthedocs.io/


Development
===========

To run all the tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
