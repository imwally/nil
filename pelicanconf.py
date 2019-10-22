#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

DEFAULT_LANG = 'en'

AUTHOR = 'Wally Jones'
SITENAME = '&Nopf;'
SITEURL = 'https://nil.wallyjones.com'
THEME = 'niltheme'
PATH = 'content'
TIMEZONE = 'America/New_York'

ARCHIVES_URL = 'archives'
ARCHIVES_SAVE_AS = 'archives/index.html'
ARTICLE_URL = '{slug}/'
ARTICLE_SAVE_AS = '{slug}/index.html'

LINKS = (('About', '/'),
         ('Archives', '/archives'),
         ('Feed', '/feeds/all.atom.xml'))

STATIC_PATHS = ['extra/robots.txt', 'extra/favicon.ico']
EXTRA_PATH_METADATA = {
    'extra/robots.txt': {'path': 'robots.txt'},
    'extra/favicon.ico': {'path': 'favicon.ico'}
}
