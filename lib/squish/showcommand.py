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

from . import progName

from command import Command
from registeredcommand import commands

import config
import bug


class ShowCommand(Command):
  '''
  Command to get init on other commands.
  '''

  command_name = 'show'
  synopsis     = 'Show a complete bug in the repository.'
  usage        = 'show [<options>] <bugnum-glob-or-partial>'

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
    bugnum   = os.path.basename(filename)
    state    = filename.split('/')[-2]

    try:
      result = bug.loadBugFromFile(filename)
    except OSError, e:
      sys.stderr.write('Unable to read %s: %s\n' % (filename, str(e)))
      return 1
    except bug.BugValidationError, e:
      filename = filename.replace(self._siteDir + '/', '')
      sys.stderr.write('%s is corrupt or invalid\n' % filename)

    print 'Bug:       %s' % bugnum
    print 'Reporter:  %s' % result.reporter
    print 'Assignee:  %s' % result.assignee
    print 'State:     %s' % state
    print 'Version:   %s' % result.version
    print 'Priority:  %s' % result.priority
    print 'Tags:      %s' % self._convertToString(result.tags)
    print 'Cc:        %s' % self._convertToString(result.cc)
    print 'Duplicate: %s' % result.duplicate
    print
    print 'Summary: %s'   % result.summary
    print
    print result.description
    print

    if not len(result.worklog):
      print 'No worklog entries.'
    else:  
      print '--- Worklog: ---'

      for entry in result.worklog:
        print 'Poster: %s' % entry.poster
        print 'Date: %s' % entry.date
        print

        for line in entry.description.split('\n'):
          print '    %s' % line

        print
        print

    return 0

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
