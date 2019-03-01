#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals
from pathlib import Path

# Home Directory
home = str(Path.home())

DEFAULT_LANG = 'en'
DEFAULT_PAGINATION = 4

AUTHOR = 'Wally Jones'
SITENAME = '&Nopf;'
SITEURL = 'http://nil.wallyjones.com'
THEME = home+'/src/niltheme'
PATH = 'content'
TIMEZONE = 'America/New_York'

ARTICLE_URL = '{slug}'
ARTICLE_SAVE_AS = '{slug}/index.html'
PAGE_URL = '{slug}'
PAGE_SAVE_AS = '{slug}/index.html'

LINKS = (('About', '/'),
         ('Archives', '/archives'),
         ('Feed', '/feeds/all.atom.xml'))
