# Copyright (c) Jack Grigg
# See LICENSE for details.

import click
from twisted.internet.task import react

from . import __version__
from .keystore import keystore


class Config(object):
    def __init__(self):
        pass

pass_config = click.make_pass_decorator(Config)

@click.group()
@click.version_option(
    message='partysig %(version)s',
    version=__version__,
)
@click.pass_context
def partysig(ctx):
    ctx.obj = cfg = Config()

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
@pass_config
def sign_start(cfg):
    from cmd_sign import alice
    with keystore(cfg) as ks:
        react(alice, (ks,))

@sign.command(name='join')
@pass_config
def sign_join(cfg):
    from cmd_sign import bob
    with keystore(cfg) as ks:
        react(bob, (ks,))

@partysig.command()
def verify():
    from cmd_verify import verify
    react(verify)
