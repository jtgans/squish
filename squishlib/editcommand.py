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
import popen2
import optparse

import yaml

from . import progName
from command import Command
from registeredcommand import commands

import config
import bug
import worklog
import emailaddress


class EditCommand(Command):
  '''
  Command to report a new bug.
  '''

  command_name = 'edit'
  synopsis     = 'Edit an existing bug.'
  usage        = 'edit [<options>] <bugnum-or-partial>'

  def __init__(self):
    Command.__init__(self)

  def _setupOptParse(self):
    pass

  def runCommand(self):
    if len(self._args) != 1:
      sys.stderr.write('edit requires a single bug number or partial.\n')
      sys.exit(1)

    bugnum = self._args[0]
    filename = self.findBugsByNumOrPartial(bugnum)

    if len(filename) > 1:
      print 'Multiple bugs matched your query.'
      print 'Please choose one from the below and retry your command.'
      print

      for bugnum in bugfiles:
        print '\t%s' % os.path.basename(bugnum)

      return 1
    else:
      filename = filename[0]

    try:
      bugreport = bug.loadBugFromFile(filename)
    except OSError, e:
      sys.stderr.write('Unable to open %s for reading: %s' % (filename, str(e)))
      sys.exit(1)
    except bug.BugValidationError, e:
      filename = filename.replace(self._siteDir + '/', '')
      sys.stderr.write('%s is an invalid or corrupt bug.' % filename)
      sys.exit(1)

    report = bugreport.generateReportTemplate()
    report = self.spawnUserEditor(report, 'bugreport.txt')

    try:
      bugreport.parseReportTemplate(report)
    except bug.BugValidationError, e:
      sys.stderr.write('Bug report validation error: %s\n' % str(e))
      sys.stderr.write('bugreport.txt left behind.\n')
      sys.exit(1)

    try:
      bug.dumpBugToFile(bugreport, filename)
    except OSError, e:
      sys.stderr.write('Unable to open %s for writing: %s\n'
                       % (self._siteDir + '/open/' + filename,
                          str(e)))
      sys.stderr.write('bugreport.txt left behind.\n')
      sys.exit(1)

    # Clean up after ourselves.
    try:
      os.unlink('bugreport.txt')
    except OSError, e:
      sys.stderr.write('Unable to unlink bugreport.txt: %s\n' % str(e))
      sys.stderr.write('bugreport.txt left behind.\n')

    print 'Bug %s updated.' % filename
    return 0

  def generateHelp(self):
    formatters = {
      'progname': progName,
      'option_help': self._parser.format_help()
      }

    return '''
Usage: %(progname)s edit [<options>] <bugnum-or-partial>

Edit an existing bug.

Note that this command spawns an editor to edit the bug report. If the report is
not changed from the original, the edit will be aborted. If bugnum-or-partial
resolves to multiple bugs, those bugs will be listed and the command will exit,
taking no action.

%(option_help)s''' % formatters
