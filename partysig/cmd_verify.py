# Copyright (c) Jack Grigg
# See LICENSE for details.

import click
from nacl.encoding import HexEncoder, RawEncoder
from nacl.exceptions import BadSignatureError
from nacl.signing import SigningKey, VerifyKey
import struct
from twisted.internet import defer

from . import util

def verify(reactor, master, msg, psig):
    version = struct.unpack('>B', psig[0])[0]
    if version != 1:
        raise ValueError('Unsupported signature version: %d' % version)

    threshold = struct.unpack('>B', psig[1])[0]
    size = struct.unpack('>B', psig[2])[0]
    if util.master_key(psig[:3+32*size]) != master:
        raise ValueError('Signature is from a different master key')

    pubkeys = [VerifyKey(psig[3+32*i:3+32*(i+1)], RawEncoder) for i in range(size)]
    sigs = [psig[3+32*size+64*i:3+32*size+64*(i+1)] for i in range(threshold)]
    for sig in sigs:
        for i in range(len(pubkeys)):
            try:
                pubkeys[i].verify(msg, sig, RawEncoder)
                pubkeys.pop(i)
                break
            except BadSignatureError:
                if i == (len(pubkeys)-1):
                    raise ValueError('Invalid signature')

    click.echo('Signature is valid!')
    return defer.succeed('ok')
