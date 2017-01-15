import pytest

def pytest_addoption(parser):
    parser.addoption("--testlogging", action='store_true')
    parser.addoption("--jmddbg", action="store_true", help="Set logger level to debug")

