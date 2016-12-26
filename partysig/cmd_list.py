# Copyright (c) Jack Grigg
# See LICENSE for details.

import click
from nacl.encoding import HexEncoder
from twisted.internet import defer


def list_keys(reactor, ks):
    for master, label in ks.list_master_keys():
        suffix = ' - %s' % label if label else ''
        click.echo('%s%s' % (HexEncoder.encode(master), suffix))
    return defer.succeed('ok')
