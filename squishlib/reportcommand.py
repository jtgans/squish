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


class ReportCommand(Command):
  '''
  Command to report a new bug.
  '''

  command_name = 'report'
  synopsis     = 'Report a new bug.'
  usage        = 'report [<options>]'

  def __init__(self):
    Command.__init__(self)

  def _setupOptParse(self):
    pass

  def runCommand(self):
    return 0

  def generateHelp(self):
    formatters = {
      'progname': progName,
      'option_help': self._parser.format_help()
      }

    return '''
Usage: %(progname)s report [<options>]

Report a new bug.

%(option_help)s''' % formatters
