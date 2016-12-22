from functools import wraps
from pyblake2 import blake2b
import struct
from wormhole.cli.public_relay import RENDEZVOUS_RELAY
from wormhole.wormhole import wormhole

APPID = u'str4d.xyz/partysig/%s'


def wormholeProto(name, relay=RENDEZVOUS_RELAY):
    def _decorator(proto):
        @wraps(proto)
        def _wormhole(reactor, *argv):
            w = wormhole(APPID % name, relay, reactor)
            d = proto(w, *argv)
            d.addBoth(w.close)
            return d
        return _wormhole
    return _decorator

def script(cfg, pubkeys):
    return struct.pack('>B', 1) + \
           struct.pack('>B', cfg.threshold) + \
           struct.pack('>B', cfg.size) + \
           b''.join(sorted(pubkeys.values()))

def master_key(script):
    return blake2b(script, digest_size=32, person=b'[partysigMaster]').digest()

def psig(script, sigs):
    return script + b''.join(sorted(sigs.values()))
