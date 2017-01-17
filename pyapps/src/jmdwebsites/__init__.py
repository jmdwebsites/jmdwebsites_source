"""Jmdwebsites

Software for building and managing a static website.
"""

# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

__author__ = "jmdwebsites"
__version__ = "0.1.1"
__copyright__ = "Copyright (c) 2016 jmdwebsites"
__license__ = "BSD 3-Clause"

from .website import Website, init_website, new_website
from .htmlpage import HtmlPage
import log
import dircmp

__all__ = ['Website', 'HtmlPage']
