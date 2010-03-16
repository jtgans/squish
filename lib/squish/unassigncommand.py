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
import hashlib
import glob
import optparse

import yaml

from . import progName

from command import Command
from registeredcommand import commands

import config
import bug
import worklog
import emailaddress


class UnassignCommand(Command):
  '''
  Command to resolve a bug.
  '''

  command_name = 'unassign'
  synopsis     = 'Unassign a bug from the current assignee.'
  usage        = 'unassign [<options>] <bug-num-or-partial>'

  def __init__(self):
    Command.__init__(self)

  def _setupOptParse(self):
    pass

  def runCommand(self):
    if len(self._args) != 1:
      sys.stderr.write('resolve requires one bug id or partial.\n')
      return 1

    bugfiles = self.findBugsByNumOrPartial(self._args[0])

    if len(bugfiles) > 1:
      print 'Multiple bugs matched your query.'
      print 'Please choose one from the below and retry your command.'
      print

      for bugnum in bugfiles:
        print '\t%s' % os.path.basename(bugnum)

      return 1

    filename = bugfiles[0]

    try:
      bugreport = bug.loadBugFromFile(filename)
    except OSError, e:
      sys.stderr.write('Unable to load %s: %s\n' % (filename, str(e)))
      sys.exit(1)
    except bug.BugValidationError, e:
      sys.stderr.write('Bug %s is invalid or corrupt. Aborting.\n'
                       % filename)
      sys.exit(1)

    bugreport.assignee = None

    try:
      bug.dumpBugToFile(bugreport, filename)
    except OSError, e:
      sys.stderr.write('Unable to dump %s to %s: %s\n'
                       % (bugnum, newfilename, str(e)))
      sys.stderr.write('Aborting.\n')
      sys.exit(1)

    print 'Bug %s unassigned.' % os.path.basename(filename)

    return 0

  def generateHelp(self):
    formatters = {
      'progname': progName,
      'option_help': self._parser.format_help()
      }

    return '''
Usage: %(progname)s resolve [<options>] <bug-num-or-partial> [<state>]

Resolve a bug to state. If bug-num-or-partial matches multiple bugs, this
command will list them and exit taking no action. If state is not specified, it
defaults to fixed.

%(option_help)s''' % formatters
