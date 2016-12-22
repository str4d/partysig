import click
from nacl.encoding import HexEncoder, RawEncoder
from nacl.signing import SigningKey, VerifyKey
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
    pk_bytes = yield w.get()
    pubkey = VerifyKey(pk_bytes, RawEncoder)
    click.echo("Participant %d's pubkey: %s" % (i, pubkey.encode(HexEncoder)))
    script = yield getScript(i, pubkey)
    yield w.send(script)

def alice(reactor, cfg):
    sk = SigningKey.generate()
    click.echo('Signing key: %s' % sk.encode(HexEncoder))
    click.echo('Pubkey: %s' % sk.verify_key.encode(HexEncoder))
    pubkeys = {0: sk.verify_key}
    pending_scripts = []

    @inlineCallbacks
    def getScript(i, pubkey):
        pubkeys[i] = pubkey
        if len(pubkeys) == cfg.size:
            script = util.script(cfg, pubkeys)
            click.echo('Script: %s' % HexEncoder.encode(script))
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
    return DeferredList([alice_channel(reactor, i, getScript) for i in range(1, cfg.size)])

@keygenProto
@inlineCallbacks
def bob(w):
    yield w.input_code('Enter code from Alice: ')
    sk = SigningKey.generate()
    click.echo('Signing key: %s' % sk.encode(HexEncoder))
    click.echo('Pubkey: %s' % sk.verify_key.encode(HexEncoder))
    yield w.send(sk.verify_key.encode(RawEncoder))
    script = yield w.get()
    click.echo('Script: %s' % HexEncoder.encode(script))
    click.echo('Master key: %s' % HexEncoder.encode(util.master_key(script)))
