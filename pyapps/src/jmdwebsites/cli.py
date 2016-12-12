import sys
import click
import jmdwebsites
from website import Website

@click.group(chain=True)
@click.option('--change-dir', '-C', default=None, help='Change working directory')
@click.option('--debug/--no-debug', '-d', default=False, help='Turn on DEBUGGING')
@click.option('--logfile', '-L', default=None, help='Turn on file logging')
def main(debug, change_dir, logfile):
    if change_dir:
        os.chdir(change_dir)
    if debug:
        click.echo('Debugging enabled.')
    jmdwebsites.log.config_logging(logfile)


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
