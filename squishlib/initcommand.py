#!/usr/bin/env python
# -*- python -*-
#
# Copyright (C) 2008  Google, Inc. All Rights Reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

'''
Squish: The stupid bug tracker.
'''

import os
import sys
import optparse

import yaml

from squishlib import commands
from squishlib import progName
from command import Command

import config
import bug

class InitCommand(Command):
  '''
  Command to get init on other commands.
  '''

  command_name = 'init'
  synopsis     = 'Initialize the squish bugs directory.'
  usage        = 'init'

  # This command doesn't need a site config to function.
  requireSiteConfig = False

  def __init__(self):
    Command.__init__(self)

  def _setupOptParse(self):
    pass

  def runCommand(self):
    try:
      os.mkdir('bugs')
    except OSError, e:
      sys.stderr.write('Unable to create bugs directory: %s\n' % str(e))
      return 1

    try:
      stream = file('bugs/config.yaml', 'w')
      yaml.dump(config.Config(), stream, default_flow_style=False)
      stream.close()
    except Exception, e:
      sys.stderr.write('Unable to create bugs/config.yaml file: %s\n' % str(e))
      return 1

    try:
      for state in bug.STATES:
        os.mkdir('bugs/%s' % state)
    except OSError, e:
      sys.stderr.write('Unable to create bugs/%s: %s\n' % (state, str(e)))
      return 1

    return 0

  def generateHelp(self):
    formatters = {
      'progname': progName,
      'option_help': self._parser.format_help()
      }

    return '''
Usage: %(progname)s init [<options>]

Initialize the bug repository. Creates a directory called 'bugs' in the current
directory, and sets up the system.

%(option_help)s''' % formatters
