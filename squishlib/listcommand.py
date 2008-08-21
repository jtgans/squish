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
    self._parser.add_option('-s', '--state', dest='state',
                            action='store',
                            default='open,reproducible',
                            help=('Restrict listings to bugs in the states '
                                  'provided. [default=%default]'))

    self._parser.add_option('-a', '--assigned-to', dest='assigned_to',
                            action='store',
                            default=None,
                            help=('Restrict listings to bugs assigned to the '
                                  'provided email address. Use the special '
                                  'keyword "me" to refer to bugs assigned to '
                                  'yourself.'))

  def runCommand(self):
    if len(self._args) > 0:
      partial = self._args[0]
    else:
      partial = '*'

    states = self._flags.state.split(',')

    if 'all' in states:
      states = bug.STATES

    if self._flags.assigned_to:
      if self._flags.assigned_to == 'me':
        assigned_to = self._userConfig.email
      else:
        try:
          assigned_to = emailaddress.EmailAddress(self._flags.assigned_to)
        except emailaddress.EmailValidationError, e:
          sys.stderr.write('%s\n' % str(e))
          sys.exit(1)

    try:
      filenames = self.findBugsByNumOrPartial(partial, states)
    except TypeError, e:
      sys.stderr.write('%s\n' % str(e))
      return 1

    for filename in filenames:
      try:
        result = bug.loadBugFromFile(filename)
        bugnum = os.path.basename(filename)
        state  = filename.split('/')[-2]

        if self._flags.assigned_to:
          if assigned_to != result.assignee:
            continue

        print 'bug %s'       % bugnum
        print 'Reporter: %s' % result.reporter
        print 'Assignee: %s' % result.assignee
        print 'State:    %s' % state
        print
        print '    %s' % result.summary
        print

      except OSError, e:
        sys.stderr.write('Unable to read %s: %s\n' % (filename, str(e)))
        return 1

      except bug.BugValidationError, e:
        filename = filename.replace(self._siteDir + '/', '')
        sys.stderr.write('%s is corrupt or invalid\n' % filename)
        continue

    return 0

  def generateHelp(self):
    formatters = {
      'progname': progName,
      'states': ', '.join(bug.STATES),
      'option_help': self._parser.format_help()
      }

    return '''
Usage: %(progname)s list [<options>] [<bugnum-glob-or-partial>]

List the bug numbers, states, assignees and summaries of bugs to stdout.

If state is not given, assume only bugs in the open and reproducable states will
be listed.

Valid states are:
  %(states)s

%(option_help)s''' % formatters
