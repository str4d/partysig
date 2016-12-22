import click
from twisted.internet.defer import inlineCallbacks

from . import util

signProto = util.wormholeProto('sign')


@signProto
@inlineCallbacks
def alice(w):
    code = yield w.get_code()
    click.echo('Give this code to Bob: %s' % code)
    yield w.send(b'm')
    yield w.send(b'P')
    sig = yield w.get()
    click.echo("Bob's sig: %s" % sig)
    yield w.send(b'1 [P1] %s' % sig)

@signProto
@inlineCallbacks
def bob(w):
    yield w.input_code('Enter code from Alice: ')
    msg = yield w.get()
    master = yield w.get()
    yield w.send(b'S1(%s|%s)' % (msg, master))
    sig = yield w.get()
    click.echo("Signature: '%s'" % sig)
