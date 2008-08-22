#!/usr/bin/env python
# -*- python -*-

import glob
import os
import os.path

from distutils.core import setup

import squishlib

setup(
  name         = 'squish',
  version      = '.'.join(map(str, squishlib.__version__)),
  description  = 'Squish: The Stupid Bug Tracker',
  author       = 'June Tate-Gans',
  author_email = 'jtgans@google.com',
  url          = 'http://squish.googlecode.com',

  package_dir  = { '': '.' },
  packages     = [ 'squishlib' ],
  scripts      = glob.glob('src/*'),
  data_files   = []
)
