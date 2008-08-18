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
import glob
import optparse

import yaml

from squishlib import commands
from squishlib import progName
from command import Command

import config
import bug


class ListCommand(Command):
  '''
  Command to get init on other commands.
  '''

  command_name = 'list'
  synopsis     = 'List existing bugs in the repository.'
  usage        = 'list [<options>] [<bugnum-glob-or-partial>]'

  def __init__(self):
    Command.__init__(self)

  def _setupOptParse(self):
    self._parser.add_option('--state', dest='state',
                            action='store', default=['open', 'reproducible'],
                            help=('Restrict listings to bugs in the states '
                                  'provided. [default=%default]'))

  def runCommand(self):
    if len(self._args) > 0:
      partial = self._args[0] + '*'
    else:
      partial = '*'

    for state in self._flags.state:
      filenames = glob.glob('%s/%s/%s' % (self._siteDir, state, partial))

      for filename in filenames:
        print os.path.basename(filename)

    return 0

  def generateHelp(self):
    formatters = {
      'progname': progName,
      'option_help': self._parser.format_help()
      }

    return '''
Usage: %(progname)s list [<options>] [<bugnum-glob-or-partial>]

List the bug numbers, states, assignees and summaries of bugs to stdout.

If state is not given, assume only bugs in the open and reproducable states will
be listed.

%(option_help)s''' % formatters
