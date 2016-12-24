# Copyright (c) Jack Grigg
# See LICENSE for details.

import errno
from functools import wraps
import os
from pyblake2 import blake2b
import stat
import struct
from wormhole.cli.public_relay import RENDEZVOUS_RELAY
from wormhole.wormhole import wormhole

APPID = u'str4d.xyz/partysig/%s'


# http://stackoverflow.com/a/15015748
def secure_file(fname, remove_existing=False):
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL  # Refer to "man 2 open".
    mode = stat.S_IRUSR | stat.S_IWUSR  # This is 0o600 in octal and 384 in decimal.

    if remove_existing:
        # For security, remove file with potentially elevated mode
        try:
            os.remove(fname)
        except OSError:
            pass

    # Open file descriptor
    umask_original = os.umask(0)
    try:
        fdesc = os.open(fname, flags, mode)
    finally:
        os.umask(umask_original)

    return fdesc

def secure_makedirs(path):
    try:
        os.makedirs(path, 0o700)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

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

def params(script):
    threshold = struct.unpack('>B', script[1])[0]
    size = struct.unpack('>B', script[2])[0]
    return (threshold, size)

def master_key(script):
    return blake2b(script, digest_size=32, person=b'[partysigMaster]').digest()

def psig(script, sigs):
    return script + b''.join(sorted(sigs.values()))
