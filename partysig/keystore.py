# Copyright (c) Jack Grigg
# See LICENSE for details.

import click
from contextlib import contextmanager
from nacl.encoding import (
    Base64Encoder,
    HexEncoder,
    RawEncoder,
)
from nacl.signing import SigningKey
import os

from . import util

@contextmanager
def keystore(cfg):
    ks = KeyStore(cfg)
    try:
        yield ks
    finally:
        ks.close()

class KeyStore(object):
    def __init__(self, cfg):
        self.cfg = cfg
        # No keygen in progress (yet)
        self.sk = None
        util.secure_makedirs(cfg.keydir)

    def close(self):
        pass

    def generate_key(self):
        self.sk = SigningKey.generate()
        return self.sk.verify_key.encode(RawEncoder)

    def save_script(self, script):
        master_hex = HexEncoder.encode(util.master_key(script))
        with os.fdopen(util.secure_file(os.path.join(self.cfg.keydir, '%s.key' % master_hex)), 'w') as f:
            f.write(self.sk.encode(Base64Encoder))
        with open(os.path.join(self.cfg.keydir, '%s.script' % master_hex), 'w') as f:
            f.write(Base64Encoder.encode(script))

    def get_script(self, master):
        master_hex = HexEncoder.encode(master)
        with open(os.path.join(self.cfg.keydir, '%s.script' % master_hex), 'r') as f:
            return Base64Encoder.decode(f.read())

    def sign(self, master, msg):
        master_hex = HexEncoder.encode(master)
        with open(os.path.join(self.cfg.keydir, '%s.key' % master_hex), 'r') as f:
            sk_hex = f.read()
        sk = SigningKey(sk_hex, Base64Encoder)
        return sk.sign(msg).signature
