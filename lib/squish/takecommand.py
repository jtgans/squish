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


class TakeCommand(Command):
  '''
  Command to report a new bug.
  '''

  command_name = 'take'
  synopsis     = 'Assign a bug to yourself.'
  usage        = 'take [<options>] <bug-num-or-partial>'

  def __init__(self):
    Command.__init__(self)

  def _setupOptParse(self):
    self._parser.add_option('-w', '--add-worklog', dest='add_worklog',
                            action='store_true',
                            default=False,
                            help=('Add a worklog entry to the bug.'))

  def runCommand(self):
    if len(self._args) != 1:
      sys.stderr.write('take requires a single bug name or partial.\n')
      return 1

    bugfiles = self.findBugsByNumOrPartial(self._args[0])

    if len(bugfiles) > 1:
      print 'Multiple bugs matched your query.'
      print 'Please choose one from the below and retry your command.'
      print

      for bugnum in bugfiles:
        print '\t%s' % os.path.basename(bugnum)

      return 1

    oldfilename = bugfiles[0]
    bugnum      = os.path.basename(oldfilename)
    newfilename = '%s/%s/%s' % (self._siteDir, 'in-progress', bugnum)

    try:
      bugreport = bug.loadBugFromFile(oldfilename)
    except OSError, e:
      sys.stderr.write('Unable to load %s: %s\n' % (oldfilename, str(e)))
      sys.exit(1)
    except bug.BugValidationError, e:
      sys.stderr.write('Bug %s is invalid or corrupt. Aborting.\n'
                       % oldfilename)
      sys.exit(1)

    if self._flags.add_worklog:
      entry = worklog.Worklog()
      entry.poster = self._userConfig.email
      entry.description = 'Taking this bug.'
      template = entry.generateReportTemplate()
      report = self.spawnUserEditor(template, 'worklog.txt')

      try:
        entry.parseReportTemplate(report)
      except worklog.WorklogValidationError, e:
        sys.stderr.write(('Worklog report validation error: '
                          '%s\n' % str(e)))
        sys.stderr.write('worklog.txt left behind\n')
        sys.exit(1)

      bugreport.worklog.append(entry)

    bugreport.assignee = self._userConfig.email

    try:
      bug.dumpBugToFile(bugreport, newfilename)
    except OSError, e:
      sys.stderr.write('Unable to dump %s to %s: %s\n'
                       % (bugnum, newfilename, str(e)))
      sys.stderr.write('Aborting.\n')
      sys.exit(1)

    try:
      os.unlink(oldfilename)

      if self._flags.add_worklog:
        os.unlink('worklog.txt')
    except OSError, e:
      sys.stderr.write('Unable to unlink %s: %s\n' % (oldfilename, str(e)))
      sys.stderr.write('Non-fatal error. Please remove %s before submitting.\n'
                       % oldfilename)

    print('Bug %s assigned to %s and marked as in-progress.'
          % (bugnum,  self._userConfig.email))

    return 0

  def generateHelp(self):
    formatters = {
      'progname': progName,
      'option_help': self._parser.format_help()
      }

    return '''
Usage: %(progname)s take [<options>] <bug-num-or-partial>

Assign a bug to yourself and move it to the in-progress state. By default,
assigning the bug to yourself moves it from whichever state it was in to
in-progress.

If bug-num-or-partial results in multiple bugs, a listing of bugs matched is
returned and no action is taken.

%(option_help)s''' % formatters
