import click
from twisted.internet import defer

def verify(reactor):
    click.echo('Verify!')
    return defer.succeed('ok')
