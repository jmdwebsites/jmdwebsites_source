import sys
import click
from website import Website
import os

@click.group(chain=True)
@click.option('--change-dir', '-C', default=None, help='Change working directory')
@click.option('--debug/--no-debug', '-d', default=False, help='Turn on DEBUGGING')
def main(debug, change_dir):
    if change_dir:
        os.chdir(change_dir)
    if debug:
        click.echo('DEBUGGING enabled.')

@main.command()
def clean():
    Website().clean()

@main.command()
def clobber():
    Website().clobber()

@main.command()
def build():
    Website().build()

if __name__ == "__main__":
    sys.exit(main())
