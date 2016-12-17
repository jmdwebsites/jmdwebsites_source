import sys
import click
from jmdwebsites import Website, new_website
import jmdwebsites
import os
import logging

logger = logging.getLogger(__name__)

def handle_error(e, severity=None):
    if severity:
        click.echo('{}: {}'.format(severity, e))
    else:
        click.echo(e)
    file_logger = logging.getLogger('file')
    if file_logger.handlers:
        file_logger.exception(e)
    
def main():
    try:
        cli()
    except jmdwebsites.website.NonFatalError as e:
        handle_error(e)
    except Exception as e:
        handle_error(e, 'fatal')
        raise
    
@click.group(chain=True)
@click.option('--logfile', '-L', default=None, help='Turn on file logging')
@click.option('--verbose', '-v', count=True, help='Verbose output')
@click.option('--debug/--no-debug', '-d', default=False, help='Turn on DEBUGGING')
@click.option('--info', is_flag=True, default=False, help='Turn on INFO messages')
@click.option('--level', default=None, help='Turn on INFO messages')
@click.option('--change-dir', '-C', default=None, help='Change working directory')
def cli(change_dir, level, info, debug, verbose, logfile):
    jmdwebsites.log.config_logging(level, info, debug, verbose, logfile)
    if logfile:
        logger.info('Logging to {}'.format(logfile))
    if change_dir:
        os.chdir(change_dir)

@cli.command()
@click.argument('site_dir')
def new(site_dir):
    new_website(site_dir)

@cli.command()
def clean():
    Website().clean()

@cli.command()
def clobber():
    Website().clobber()

@cli.command()
def build():
    Website().build()

if __name__ == "__main__":
    sys.exit(main())
