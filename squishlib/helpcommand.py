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

from . import showSquishUsage
from . import generateSquishUsage
from . import commands
from . import progName
from command import Command


class HelpCommand(Command):
  '''
  Command to get help on other commands.
  '''

  command_name = 'help'
  synopsis     = 'Get help on other commands.'
  usage        = 'help [<options>] <command>'

  def __init__(self):
    Command.__init__(self)

  def _setupOptParse(self):
    pass

  def runCommand(self):
    if len(self._args) < 2:
      showSquishUsage(self._parser.format_help())
      return 1

    cmd = sys.argv[2]

    if cmd not in commands.keys():
      print '%s is not a valid command.\n'
      showSquishUsage(self._parser.format_help())
      return 1

    cmd = commands[cmd]()
    print '%s - %s\n\n%s' % (cmd.command_name,
                             cmd.synopsis,
                             cmd.generateHelp())

    return 0

  def generateHelp(self):
    formatters = {
      'progname': progName,
      'option_help': self._parser.format_help()
      }

    return '''
Usage: %(progname)s help [<options>] <command>

Where <command> is one of the available commands squish has.

Simply call this command with an argument of the command you want further
information on, and it will print it out for you on stdout. Given no
arguments, this command will print help containing a listing of global
options and registered commands.

%(option_help)s''' % formatters
