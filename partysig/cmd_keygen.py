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
def alice_channel(w, d_ui, i, getScript):
    code = yield w.get_code()
    click.echo('- %s' % code)
    d_ui.callback(None)
    pubkey = yield w.get()
    script = yield getScript(i, pubkey)
    yield w.send(script)

def alice(reactor, cfg, ks):
    pubkeys = {0: ks.generate_key()}
    pending_scripts = []

    bar = []
    def create_bar(length):
        bar.append(click.progressbar(length=length,
                                     label='Waiting for participants',
                                     show_eta=False))
        bar[0].render_progress()
    def update_bar(length):
        if bar:
            bar[0].update(length)
    def finish_bar():
        if bar:
            bar[0].render_finish()
    d_ui = [Deferred() for i in xrange(1, cfg.size)]
    ui = DeferredList(d_ui)
    ui.addCallback(lambda _: create_bar(cfg.size-1))
    ui.addErrback(lambda _: finish_bar())

    @inlineCallbacks
    def getScript(i, pubkey):
        pubkeys[i] = pubkey
        update_bar(len(pubkeys)-1)
        if len(pubkeys) == cfg.size:
            finish_bar()
            script = util.script(cfg, pubkeys)
            ks.save_script(script)
            click.echo('Key generated!')
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
    d = DeferredList([alice_channel(reactor, d_ui[i-1], i, getScript) for i in xrange(1, cfg.size)],
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
    click.echo('Key generated!')
    click.echo('Master key: %s' % HexEncoder.encode(util.master_key(script)))
