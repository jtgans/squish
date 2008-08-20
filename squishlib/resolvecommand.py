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
import sha
import glob
import optparse

import yaml

from squishlib import commands
from squishlib import progName
from command import Command

import config
import bug
import worklog
import emailaddress


class ResolveCommand(Command):
  '''
  Command to resolve a bug.
  '''

  command_name = 'resolve'
  synopsis     = 'Mark a bug as resolved.'
  usage        = 'resolve [<options>] <bug-num-or-partial> [<state>]'

  def __init__(self):
    Command.__init__(self)

  def _setupOptParse(self):
    self._parser.add_option('-u', '--unassign', dest='unassign',
                            action='store_true',
                            default=False,
                            help=('If the specified bug is assigned to '
                                  'someone, unassign it.'))

    self._parser.add_option('-w', '--add-worklog', dest='add_worklog',
                            action='store_true',
                            default=False,
                            help=('Add a worklog entry to the bug.'))

    self._parser.add_option('-m', '--add-worklog-message', dest='add_worklog',
                            action='store', type='string',
                            default=False,
                            help=('Add a worklog entry to the bug directly '
                                  'from the command line.'))

  def runCommand(self):
    if len(self._args) < 1 or len(self._args) > 2:
      sys.stderr.write('resolve requires at least a bug name or partial.\n')
      return 1

    bugfiles = self.findBugsByNumOrPartial(self._args[0])

    if len(bugfiles) > 1:
      print 'Multiple bugs matched your query.'
      print 'Please choose one from the below and retry your command.'
      print

      for bugnum in bugfiles:
        print '\t%s' % os.path.basename(bugnum)

      return 1

    if len(self._args) == 2:
      state = self._args[1]

      if state not in bug.STATES:
        sys.stderr.write('%s is not a valid bug state.\n' % state)
        sys.stderr.write('Valid states are %s.\n', ', '.join(bug.STATES))
        sys.exit(1)
    else:
      state = 'fixed'

    oldfilename = bugfiles[0]
    bugnum      = os.path.basename(oldfilename)
    newfilename = '%s/%s/%s' % (self._siteDir, state, bugnum)

    try:
      bugreport = bug.loadBugFromFile(oldfilename)
    except OSError, e:
      sys.stderr.write('Unable to load %s: %s\n' % (oldfilename, str(e)))
      sys.exit(1)
    except bug.BugValidationError, e:
      sys.stderr.write('Bug %s is invalid or corrupt. Aborting.\n'
                       % oldfilename)
      sys.exit(1)

    # TODO(jtg): Add code for adding the worklog
    if self._flags.add_worklog:
      if isinstance(self._flags.add_worklog, str):
        # TODO(jtg): Add code to read the worklog straight from the command
        # line.
        pass

      else:
        self.spawnUserEditor('', 'worklog.txt')

    if self._flags.unassign:
      bugreport.assignee = None

    try:
      bug.dumpBugToFile(bugreport, newfilename)
    except OSError, e:
      sys.stderr.write('Unable to dump %s to %s: %s\n'
                       % (bugnum, newfilename, str(e)))
      sys.stderr.write('Aborting.\n')
      sys.exit(1)

    try:
      os.unlink(oldfilename)
    except OSError, e:
      sys.stderr.write('Unable to unlink %s: %s\n' % (oldfilename, str(e)))
      sys.stderr.write('Non-fatal error. Please remove %s before submitting.\n'
                       % oldfilename)

    print 'Bug %s updated and marked as as %s.' % (bugnum,  state)

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
