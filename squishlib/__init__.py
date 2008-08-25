#!/usr/bin/env python
# -*- python -*-
# pylint: disable-msg=W0122
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

Library initializer and location for global variables for the entire suite of
utilities.
'''

import os
import yaml


__version__  = (0, 2)

progName = None


def generateSquishUsage(additional_help=None):
  '''
  Generate the usage string for the general squish executable.
  '''

  usage  = 'Usage: \n'
  usage += '  %s <command> [<options>] [<arguments>]\n\n' % progName
  usage += 'Commands registered:\n\n'

  names = commands.keys()
  names.sort()

  for name in names:
    usage += '  %s\n    %s\n\n' % (commands[name].usage,
                                   commands[name].synopsis)

  if additional_help:
    usage += '%s\n' % additional_help

  usage += ('Use %s help <command> for more information on a '
            'command.\n') % progName

  return usage


def showSquishUsage(additional_help=None):
  '''
  Print out the usage for the general squish executable.
  '''

  print generateSquishUsage(additional_help)


# Force importing all of the classes into the toplevel squish module namespace.
for filename in os.listdir(__path__[0]):
  if ('__init__' not in filename
      and '.py' in filename
      and '#' not in filename):
    filename, ext = filename.split('.')    # Strip off the extension
    exec 'from %s import *' % filename     # Then import it
