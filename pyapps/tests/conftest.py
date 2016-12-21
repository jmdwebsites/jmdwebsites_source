import pytest

def pytest_addoption(parser):
    parser.addoption("--testlogging", action='store_true')

