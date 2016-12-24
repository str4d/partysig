# Copyright (c) Jack Grigg
# See LICENSE for details.

import click
from contextlib import contextmanager
from nacl.encoding import HexEncoder, RawEncoder
from nacl.signing import SigningKey

@contextmanager
def keystore(cfg):
    ks = KeyStore(cfg)
    try:
        yield ks
    finally:
        ks.close()

class KeyStore(object):
    def __init__(self, cfg):
        # No keygen in progress (yet)
        self.sk = None

    def close(self):
        pass

    def generate_key(self):
        self.sk = SigningKey.generate()
        click.echo('Signing key: %s' % self.sk.encode(HexEncoder))
        click.echo('Pubkey: %s' % self.sk.verify_key.encode(HexEncoder))
        return self.sk.verify_key.encode(RawEncoder)

    def save_script(self, script):
        click.echo('Script: %s' % HexEncoder.encode(script))

    def get_script(self, master):
        script_hex = click.prompt('Enter script for master key %s' % HexEncoder.encode(master))
        return HexEncoder.decode(script_hex)

    def sign(self, master, msg):
        sk_hex = click.prompt('Enter signing key for master key %s' % HexEncoder.encode(master))
        sk = SigningKey(sk_hex, HexEncoder)
        return sk.sign(msg).signature
