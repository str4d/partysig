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

Usage
=====

Key generation
--------------

On one machine, run::

    $ partysig keygen start

On the other machines, run::

    $ partysig keygen join

Signing
-------

On the machine with the file to sign, run::

    $ partysig sign start FILE

On the other machines, run::

    $ partysig sign join

Verifying signatures
--------------------

Run::

    $ partysig verify FILE SIGNATURE

Design
======

The current signature version (v1) implements Bitcoin-style multi-sig, where the overall
multisignature contains:

- The number of signatures required for the multisignature to be valid
- The public keys allowed to create signatures
- Signatures from a subset of those keys

The first two parts together are equivalent to a Bitcoin script, and are similarly hashed
to get the "master key" for the multi-party signature group. Ed25519 is used for the
individual signatures, and BLAKE2b is used for creating the master key.

Signature format
----------------

::

    Version    (1-byte uint)     \
    Threshold  (1-byte uint)      |_ Hashed to obtain
    Size       (1-byte uint)      |  the master key
    Pubkeys    (32 x size bytes) /
    Signatures (64 x threshold bytes)

Acknowledgements
================

- `Joanna Rutkowska`_ asked `the question`_ that prompted the creation of this tool.
- `Brian Warner`_ wrote `Magic Wormhole`_, which is a key component to this tool's usability.

.. _`Joanna Rutkowska`: https://blog.invisiblethings.org/
.. _`the question`: https://twitter.com/rootkovska/status/806553962770006019
.. _`Brian Warner`: http://www.lothar.com/
.. _`Magic Wormhole`: https://github.com/warner/magic-wormhole
