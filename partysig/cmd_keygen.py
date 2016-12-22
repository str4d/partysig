import click
from twisted.internet.defer import inlineCallbacks

from . import util

keygenProto = util.wormholeProto('keygen')


@keygenProto
@inlineCallbacks
def alice(w):
    code = yield w.get_code()
    click.echo('Give this code to Bob: %s' % code)
    pubkey = yield w.get()
    click.echo("Bob's pubkey: %s" % pubkey)
    yield w.send(b'1 [%s]' % pubkey)

@keygenProto
@inlineCallbacks
def bob(w):
    yield w.input_code('Enter code from Alice: ')
    yield w.send(b'P1')
    script = yield w.get()
    click.echo("Script: '%s'" % script)
