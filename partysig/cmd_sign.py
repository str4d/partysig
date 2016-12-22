import click
import os
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
def alice_channel(w, i, getPSig):
    code = yield w.get_code()
    click.echo('- %s' % code)
    yield w.send(b'm')
    yield w.send(b'P')
    sig = yield w.get()
    click.echo("Participant %d's sig: %s" % (i, sig))
    psig = yield getPSig(i, sig)
    yield w.send(psig)

def alice(reactor, cfg):
    sigs = {0: 'S0(m|P)'}
    pending_psigs = []
    generated_psig = [] # List so we can set inside nested function

    @inlineCallbacks
    def getPSig(i, sig):
        sigs[i] = sig
        if len(sigs) == cfg.threshold:
            click.echo('Threshold reached, generating signature')
            psig = b'1 [%s] [%s]' % (', '.join(['P%d' % j for j in sigs.keys()]),
                                     ', '.join(sigs.values()))
            click.echo("Signature: '%s'" % psig)
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
    return DeferredList([alice_channel(reactor, i, getPSig) for i in range(1, cfg.size)])

@signProto
@inlineCallbacks
def bob(w):
    yield w.input_code('Enter code from Alice: ')
    msg = yield w.get()
    master = yield w.get()
    yield w.send(b'S%d(%s|%s)' % (os.getpid(), msg, master))
    sig = yield w.get()
    click.echo("Signature: '%s'" % sig)
