========
partysig
========

A command-line tool for creating and verifying distributed multi-party signatures.

Installation
============

::

    $ pip install partysig

Usage
=====

Key generation
--------------

On one machine, run::

    $ partysig keygen start [--size=N] [--threshold=K] [SOME LABEL]

Example output::

    Give one code to each participant:
    - 5-recipe-adult
    - 4-potato-gremlin
    Waiting for participants  [####################################]  100%
    Key generated!
    Master key: MASTER_KEY

On the other machines, run::

    $ partysig keygen join [SOME LABEL]

Example output::

    Enter code from Alice: 5-recipe-adult
    Key generated!
    Master key: MASTER_KEY

    Enter code from Alice: 4-potato-gremlin
    Key generated!
    Master key: MASTER_KEY

Signing
-------

On the machine with the file to sign, run::

    $ partysig sign start --key=MASTER_KEY FILE

Example output::

    Give one code to each participant:
    - 1-aftermath-pheasant
    - 2-document-framework
    Waiting for signers  [####################################]  100%
    Threshold reached!
    Signature: SIGNATURE

On the other machines, run::

    $ partysig sign join
    Enter code from Alice: 1-aftermath-pheasant
    Waiting for signers...
    Threshold reached!
    Signature: SIGNATURE

    $ partysig sign join
    Enter code from Alice: 2-document-framework
    Waiting for signers...
    Threshold reached!
    Signature: SIGNATURE

Verifying signatures
--------------------

Run::

    $ partysig verify FILE SIGNATURE

Example output::

    Signature is valid!

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
