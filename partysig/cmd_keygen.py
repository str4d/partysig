import click
import os
from twisted.internet.defer import (
    Deferred,
    DeferredList,
    inlineCallbacks,
    returnValue,
)

from . import util

keygenProto = util.wormholeProto('keygen')


@keygenProto
@inlineCallbacks
def alice_channel(w, i, getScript):
    code = yield w.get_code()
    click.echo('- %s' % code)
    pubkey = yield w.get()
    click.echo("Participant %d's pubkey: %s" % (i, pubkey))
    script = yield getScript(i, pubkey)
    yield w.send(script)

def alice(reactor, cfg):
    pubkeys = {0: 'P0'}
    pending_scripts = []

    @inlineCallbacks
    def getScript(i, pubkey):
        pubkeys[i] = pubkey
        if len(pubkeys) == cfg.size:
            script = b'1 [%s]' % ', '.join(pubkeys.values())
            click.echo("Script: '%s'" % script)
            for d in pending_scripts:
                d.callback(script)
            returnValue(script)
        else: # Still accumulating
            d = Deferred()
            pending_scripts.append(d)
            script = yield d
            returnValue(script)

    click.echo('Give one code to each participant:')
    return DeferredList([alice_channel(reactor, i, getScript) for i in range(1, cfg.size)])

@keygenProto
@inlineCallbacks
def bob(w):
    yield w.input_code('Enter code from Alice: ')
    yield w.send(b'P%d' % os.getpid())
    script = yield w.get()
    click.echo("Script: '%s'" % script)
