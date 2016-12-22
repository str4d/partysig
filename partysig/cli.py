import click
from twisted.internet.task import react

from . import __version__


@click.group()
@click.version_option(
    message='partysig %(version)s',
    version=__version__,
)
def partysig():
    pass

@partysig.group()
def keygen():
    pass

@keygen.command(name='start')
def keygen_start():
    from cmd_keygen import alice
    react(alice)

@keygen.command(name='join')
def keygen_join():
    from cmd_keygen import bob
    react(bob)

@partysig.group()
def sign():
    pass

@sign.command(name='start')
def sign_start():
    from cmd_sign import alice
    react(alice)

@sign.command(name='join')
def sign_join():
    from cmd_sign import bob
    react(bob)

@partysig.command()
def verify():
    from cmd_verify import verify
    react(verify)
