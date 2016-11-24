import pytest
from jmdwebsites.website import Website

@pytest.fixture()
def setup():
    print("")

def test_clobber_then_build(setup):
    website = Website()
    website.clobber()
    website.build()

def test_other(setup):
    print "Test other stuff!"
    

