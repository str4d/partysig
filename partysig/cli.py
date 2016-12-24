# Copyright (c) Jack Grigg
# See LICENSE for details.

import click
from nacl.encoding import HexEncoder
import os
from twisted.internet.task import react

from . import __version__, util
from .keystore import keystore

APP_NAME = 'partysig'
SUBDIRS = {
    'keydir': 'keys',
}


class Config(object):
    def __init__(self):
        pass

pass_config = click.make_pass_decorator(Config)

def confdir_defaults(ctx, param, value):
    for p in ctx.command.params:
        if isinstance(p, click.Option) and p.name.endswith('dir') and p != param:
            p.default = os.path.join(value, SUBDIRS[p.name])
    return value

@click.group()
@click.option('--confdir', type=click.Path(), default=click.get_app_dir(APP_NAME),
              is_eager=True, callback=confdir_defaults,
              help='base location to store configuration data on this machine')
@click.option('--keydir', type=click.Path(),
              help='location to store the signing keys generated on this machine (default: $confdir/keys)')
@click.version_option(
    message='partysig %(version)s',
    version=__version__,
)
@click.pass_context
def partysig(ctx, confdir, keydir):
    ctx.obj = cfg = Config()
    cfg.confdir = confdir
    cfg.keydir = keydir

@partysig.group()
def keygen():
    pass

@keygen.command(name='start')
@click.option('--size', default=3,
              help='number of participants who can sign')
@click.option('--threshold', default=2,
              help='minimum number of participants required to create a signature')
@pass_config
def keygen_start(cfg, size, threshold):
    cfg.size = size
    cfg.threshold = threshold
    from cmd_keygen import alice
    with keystore(cfg) as ks:
        react(alice, (cfg, ks))

@keygen.command(name='join')
@pass_config
def keygen_join(cfg):
    from cmd_keygen import bob
    with keystore(cfg) as ks:
        react(bob, (ks,))

@partysig.group()
def sign():
    pass

@sign.command(name='start')
@click.option('--key', prompt=True)
@click.argument('msg', type=click.File('rb'))
@pass_config
def sign_start(cfg, key, msg):
    from cmd_sign import alice
    with keystore(cfg) as ks:
        react(alice, (ks, HexEncoder.decode(key), msg.read()))

@sign.command(name='join')
@pass_config
def sign_join(cfg):
    from cmd_sign import bob
    with keystore(cfg) as ks:
        react(bob, (ks,))

@partysig.command()
@click.option('--key', prompt=True)
@click.argument('msg', type=click.File('rb'))
@click.argument('signature')
def verify(key, msg, signature):
    from cmd_verify import verify
    react(verify, (HexEncoder.decode(key), msg.read(), HexEncoder.decode(signature)))
