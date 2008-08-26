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
import os.path
import sys
import glob
import optparse

import yaml

from . import progName

from command import Command
from registeredcommand import commands

import config
import bug
import worklog


class UpdateCommand(Command):
  '''
  Command to get init on other commands.
  '''

  command_name = 'update'
  synopsis     = 'Update a bug by adding a worklog entry to it.'
  usage        = 'update [<options>] <bugnum-glob-or-partial>'

  def __init__(self):
    Command.__init__(self)

  def _setupOptParse(self):
    pass

  def runCommand(self):
    if len(self._args) > 0:
      partial = self._args[0]
    else:
      partial = '*'

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
      sys.stderr.write('Unable to read %s: %s\n' % (filename, str(e)))
      return 1
    except bug.BugValidationError, e:
      filename = filename.replace(self._siteDir + '/', '')
      sys.stderr.write('%s is corrupt or invalid\n' % filename)

    entry = worklog.Worklog()
    entry.poster = self._userConfig.email
    template = entry.generateReportTemplate()

    # Let the user and the scripts have at the template
    report = self.runScripts('pre-update', template)
    report = self.spawnUserEditor(report, 'worklog.txt')
    report = self.runScripts('post-update', report)

    try:
      entry.parseReportTemplate(report)
    except worklog.WorklogValidationError, e:
      sys.stderr.write(('Worklog report validation error: '
                        '%s\n' %  str(e)))
      sys.stderr.write('worklog.txt left behind\n')
      sys.exit(1)

    bugreport.worklog.append(entry)

    try:
      bug.dumpBugToFile(bugreport, filename)
    except OSError, e:
      sys.stderr.write('Unable to open %s for writing: %s\n'
                       % (filename, str(e)))
      sys.stderr.write('worklog.txt left behind.\n')
      sys.exit(1)

    # Clean up after ourselves.

    try:
      os.unlink('worklog.txt')
    except OSError, e:
      sys.stderr.write('Unable to unlink worklog.txt: %s\n' % str(e))
      sys.stderr.write('Non-fatal, but you\'ll need to unlink it if you want\n')
      sys.stderr.write('to report another bug.\n')

    print 'Bug %s updated.' % os.path.basename(filename)
    return 0

  def runScripts(self, kind, template):
    # TODO(jtg): Fix this -- we want pre and post scripts for update
    # as well as report.
    return template

  def _convertToString(self, var):
    '''
    Quick method to return a proper string. Handles lists, strings,
    None, and unknown types gracefully.

    Typically used for format strings. Ie:

      print '%s' % self._convertToString(foo)
    '''

    if isinstance(var, list):
      return ', '.join(var)
    elif isinstance(var, str):
      return var
    elif var == None:
      return 'None'
    else:
      return 'Unknown type %s' % type(var)

  def generateHelp(self):
    formatters = {
      'progname': progName,
      'option_help': self._parser.format_help()
      }

    return '''
Usage: %(progname)s show [<options>] <bugnum-glob-or-partial>

Show the entirety of a bug report to stdout.

If bug-num-or-partial matches multiple bugs, this command will list
them and exit taking no action.

%(option_help)s''' % formatters
