import click

class Website(object):
    
    def __init__(self):
        #click.echo('Instantiate App.')
        pass

    def clean(self):
        """Clean up the build."""
        click.echo(self.clean.__doc__)

    def clobber(self):
        """Clobber the build removing everything."""
        click.echo(self.clobber.__doc__)

    def build(self):
        """Build the project."""
        click.echo(self.build.__doc__)
