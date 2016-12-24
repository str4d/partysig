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

signProto = util.wormholeProto('sign')


@signProto
@inlineCallbacks
def alice_channel(w, i, msg, master, getPSig):
    code = yield w.get_code()
    click.echo('- %s' % code)
    yield w.send(master)
    yield w.send(msg)
    sig = yield w.get()
    click.echo("Participant %d's sig: %s" % (i, HexEncoder.encode(sig)))
    psig = yield getPSig(i, sig)
    yield w.send(psig)

def alice(reactor, ks):
    msg = b'This is a message.'
    master = HexEncoder.decode(click.prompt('Master key'))
    script = ks.get_script(master)
    threshold, size = util.params(script)
    sigs = {0: ks.sign(master, msg)}
    pending_psigs = []
    generated_psig = [] # List so we can set inside nested function

    @inlineCallbacks
    def getPSig(i, sig):
        sigs[i] = sig
        if len(sigs) == threshold:
            click.echo('Threshold reached')
            psig = util.psig(script, sigs)
            click.echo('Signature: %s' % HexEncoder.encode(psig))
            generated_psig.append(psig)
            for d in pending_psigs:
                d.callback(psig)
            returnValue(psig)
        elif generated_psig:
            returnValue(generated_psig[0])
        else: # Still accumulating
            d = Deferred()
            pending_psigs.append(d)
            psig = yield d
            returnValue(psig)

    click.echo('Give one code to each participant:')
    d = DeferredList([alice_channel(reactor, i, msg, master, getPSig) for i in range(1, size)],
                     fireOnOneErrback=True)
    def _errback(failure):
        click.echo(failure)
        return failure
    d.addErrback(_errback)
    return d

@signProto
@inlineCallbacks
def bob(w, ks):
    yield w.input_code('Enter code from Alice: ')
    master = yield w.get()
    msg = yield w.get()
    yield w.send(ks.sign(master, msg))
    psig = yield w.get()
    click.echo('Signature: %s' % HexEncoder.encode(psig))
