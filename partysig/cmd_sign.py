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
def alice_channel(w, d_ui, i, msg, master, getPSig):
    code = yield w.get_code()
    click.echo('- %s' % code)
    d_ui.callback(None)
    yield w.send(master)
    yield w.send(msg)
    sig = yield w.get()
    psig = yield getPSig(i, sig)
    yield w.send(psig)

def alice(reactor, ks, master, msg):
    script = ks.get_script(master)
    threshold, size = util.params(script)
    sigs = {0: ks.sign(master, msg)}
    pending_psigs = []
    generated_psig = [] # List so we can set inside nested function

    bar = []
    def create_bar(length):
        bar.append(click.progressbar(length=length,
                                     label='Waiting for signers',
                                     show_eta=False))
        bar[0].render_progress()
    def update_bar(length):
        if bar:
            bar[0].update(length)
    def finish_bar():
        if bar:
            bar[0].render_finish()
    d_ui = [Deferred() for i in xrange(1, size)]
    ui = DeferredList(d_ui)
    ui.addCallback(lambda _: create_bar(threshold-1))
    ui.addErrback(lambda _: finish_bar())

    @inlineCallbacks
    def getPSig(i, sig):
        sigs[i] = sig
        update_bar(len(sigs)-1)
        if len(sigs) == threshold:
            finish_bar()
            psig = util.psig(script, sigs)
            click.echo('Threshold reached!')
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
    d = DeferredList([alice_channel(reactor, d_ui[i-1], i, msg, master, getPSig) for i in xrange(1, size)],
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
    click.echo('Threshold reached!')
    click.echo('Signature: %s' % HexEncoder.encode(psig))
