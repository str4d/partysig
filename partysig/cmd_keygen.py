# Copyright (c) Jack Grigg
# See LICENSE for details.

import click
from nacl.encoding import HexEncoder
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
    click.echo("Participant %d's pubkey: %s" % (i, HexEncoder.encode(pubkey)))
    script = yield getScript(i, pubkey)
    yield w.send(script)

def alice(reactor, cfg, ks):
    pubkeys = {0: ks.generate_key()}
    pending_scripts = []

    @inlineCallbacks
    def getScript(i, pubkey):
        pubkeys[i] = pubkey
        if len(pubkeys) == cfg.size:
            script = util.script(cfg, pubkeys)
            ks.save_script(script)
            click.echo('Master key: %s' % HexEncoder.encode(util.master_key(script)))
            for d in pending_scripts:
                d.callback(script)
            returnValue(script)
        else: # Still accumulating
            d = Deferred()
            pending_scripts.append(d)
            script = yield d
            returnValue(script)

    click.echo('Give one code to each participant:')
    d = DeferredList([alice_channel(reactor, i, getScript) for i in range(1, cfg.size)],
                     fireOnOneErrback=True)
    def _errback(failure):
        click.echo(failure)
        return failure
    d.addErrback(_errback)
    return d

@keygenProto
@inlineCallbacks
def bob(w, ks):
    yield w.input_code('Enter code from Alice: ')
    yield w.send(ks.generate_key())
    script = yield w.get()
    ks.save_script(script)
    click.echo('Master key: %s' % HexEncoder.encode(util.master_key(script)))
