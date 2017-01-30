from __future__ import print_function

import sys
import click
from jmdwebsites import Website, init_website, new_website
import jmdwebsites
import os
import logging

logger = logging.getLogger(__name__)

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
    

def handle_error(e, severity=None):
    if severity:
        eprint('{}: {}'.format(severity, e))
    else:
        eprint(e)
    file_logger = logging.getLogger('file')
    if file_logger.handlers:
        file_logger.exception(e)
    
def main():
    try:
        cli()
    except jmdwebsites.website.NonFatalError as e:
        handle_error(e)
    except jmdwebsites.website.ProjectNotFoundError as e:
        eprint(e)
        sys.exit(1)
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
        try:
            os.chdir(change_dir)
        except OSError as e:
            eprint('{}: {}'.format(e.filename, e.strerror))
            sys.exit(1)

@cli.command()
#@click.argument('name')
@click.option('--name', '-n', default='', help='Select site name')
def new(name):
    try:
        new_website(name)
    except jmdwebsites.website.PathAlreadyExists as e:
        eprint('new:', e)

@cli.command()
def init():
    try:
        init_website()
    except jmdwebsites.website.WebsiteProjectAlreadyExists as e:
        eprint('new:', e)

@cli.command()
def clean():
    Website().clean()

@cli.command()
def clobber():
    try:
        website = Website()
        website.clobber()
    except jmdwebsites.website.PathNotFoundError as e:
        eprint('clobber: No such build dir: {}'.format(website.build_dir))
        sys.exit(1)

@cli.command()
def build():
    Website().build()

if __name__ == "__main__":
    sys.exit(main())
