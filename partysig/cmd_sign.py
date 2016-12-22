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

def alice(reactor, cfg):
    msg = b'This is a message.'
    script_hex = click.prompt('Enter script')
    script = HexEncoder.decode(script_hex)
    master = util.master_key(script)
    sk_hex = click.prompt('Enter signing key for master key %s' % HexEncoder.encode(master))
    sk = SigningKey(sk_hex, HexEncoder)
    sig = sk.sign(msg).signature
    sigs = {0: sig}
    pending_psigs = []
    generated_psig = [] # List so we can set inside nested function

    @inlineCallbacks
    def getPSig(i, sig):
        sigs[i] = sig
        if len(sigs) == cfg.threshold:
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
    return DeferredList([alice_channel(reactor, i, msg, master, getPSig) for i in range(1, cfg.size)])

@signProto
@inlineCallbacks
def bob(w):
    yield w.input_code('Enter code from Alice: ')
    master = yield w.get()
    msg = yield w.get()
    sk_hex = click.prompt('Enter signing key for master key %s' % HexEncoder.encode(master))
    sk = SigningKey(sk_hex, HexEncoder)
    sig = sk.sign(msg).signature
    yield w.send(sig)
    psig = yield w.get()
    click.echo('Signature: %s' % HexEncoder.encode(psig))
