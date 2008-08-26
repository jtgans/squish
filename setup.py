#!/usr/bin/env python
# -*- python -*-

import os
import os.path
import sys
import glob

from distutils.core import setup

# Make sure that squish can be imported properly.
sys.path.append('lib')
import squish

setup(
  name         = 'squish',
  version      = '.'.join(map(str, squish.__version__)),
  description  = 'Squish: The Stupid Bug Tracker',
  author       = 'June Tate-Gans',
  author_email = 'jtgans@google.com',
  url          = 'http://squish.googlecode.com',

  package_dir  = { '': '.' },
  packages     = [ 'squish' ],
  scripts      = glob.glob('src/*'),
  data_files   = []
)
