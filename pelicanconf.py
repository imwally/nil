#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals
from pathlib import Path

# Home Directory
home = str(Path.home())

AUTHOR = 'Wally Jones'
SITENAME = '&Nopf;'
SITEURL = ''
THEME = home+'/src/niltheme'
PATH = 'content'
TIMEZONE = 'America/New_York'

DEFAULT_LANG = 'en'
DEFAULT_PAGINATION = 4

LINKS = (('About', '/'),
         ('Archives', '/archives.html'),
         ('Feed', '/feeds/all.atom.xml'))
