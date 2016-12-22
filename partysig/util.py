from functools import wraps
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
