========
partysig
========

A command-line tool for creating and verifying distributed multi-party signatures.

Installation
============

::

    $ virtualenv env
    $ . env/bin/activate
    $ pip install -e .

Design
======

The current signature version (v1) implements Bitcoin-style multi-sig, where the overall
multisignature contains:

- The number of signatures required for the multisignature to be valid
- The public keys allowed to create signatures
- Signatures from a subset of those keys

The first two parts together are equivalent to a Bitcoin script, and are similarly hashed
to get the "master key" for the multi-party signature group.

Acknowledgements
================

- `Joanna Rutkowska`_ asked `the question`_ that prompted the creation of this tool.
- `Brian Warner`_ wrote `Magic Wormhole`_, which is a key component to this tool's usability.

.. _`Joanna Rutkowska`: https://blog.invisiblethings.org/
.. _`the question`: https://twitter.com/rootkovska/status/806553962770006019
.. _`Brian Warner`: http://www.lothar.com/
.. _`Magic Wormhole`: https://github.com/warner/magic-wormhole
