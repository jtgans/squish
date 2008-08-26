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

import re
import sys
import yaml
import datetime
import cStringIO

import emailaddress


class WorklogValidationError(Exception):
  '''
  An error thrown when a worklog entry does not validate.
  '''

  pass


class Worklog(yaml.YAMLObject):
  '''
  A single worklog entry. Bugs typically have zero or more of these.
  '''

  yaml_tag = '!worklog'

  _separatorPattern = re.compile(ur'^---[\w\s]+---$')
  _headerPattern    = re.compile(ur'^(\w+): (.*)$')

  def __init__(self):
    self.poster = None
    self.date = datetime.datetime.utcnow()
    self.description = None

  def __repr__(self):
    return ('%s(poster=%s, date=%s, description=%s)'
            % (self.__class__.__name__,
               self.poster,
               self.date.isoformat(),
               self.description))

  def _varOrBlank(self, var):
    '''
    Return either the variable provided, or return a blank string.

    This is to fix Python's annoying habit of converting None types to the word
    None instead of the empty string.

    Additionally combines lists into a comma-separated list.
    '''

    if var:
      if isinstance(var, list):
        return ', '.join(var)
      else:
        return var

    return ''

  def generateReportTemplate(self):
    '''
    Generates a new bug report template containing whatever was set in the
    object directly before this method was called. Should be handed off to the
    user's favorite editor and then passed on to parseReportTemplate.
    '''

    oldstdout = sys.stdout
    sys.stdout = cStringIO.StringIO()

    print 'Poster: %s'  % self._varOrBlank(self.poster)
    print '---worklog update follows this line---'
    print '%s\n' % self._varOrBlank(self.description)
    print '# Put your worklog entry body here.'
    print '#'
    print '# Lines beginning with hash marks (like these) are ignored and will'
    print '# not be included in the description of the bug.'
    print '#'
    print '# Fields that are absolutely required are Reporter and the body.'
    print '# If either of those fields are left empty, the worklog update'
    print '# will be aborted.'
    print '#'
    print '# If this file remains unchanged, the bug report will be aborted.'

    report = sys.stdout.getvalue()
    sys.stdout.close()
    sys.stdout = oldstdout

    return report

  def parseReportTemplate(self, report):
    '''
    Given a bug report template of the form:

       Header: value
       ...
       ---separator---
       Description body

    Parse the values into this bug, and validate that the values are correct.
    '''

    # Toggle so that when we pass the separator we can start consuming the
    # body.
    in_body = False

    # Generate a list of valid headers
    valid_headers = filter(lambda key: not key.startswith('_'),
                           self.__dict__.keys())

    # Split the report into seperate lines
    report = report.splitlines()

    # Iterate over the headers and set our internal values until we reach the
    # dividing line.
    for line in report:
      if self._separatorPattern.match(line):
        self.description = ''
        in_body = True
        continue          # skip the separator

      if not in_body:
        splitpos = line.find(':')

        if splitpos == -1:
          raise BugValidationError('%s is not a valid line.' % line)

        key = line[:splitpos].strip().lower()
        val = line[splitpos+1:].strip()

        if key not in valid_headers:
          raise BugValidationError('Line %s is not a known line.' % key)

        if val == '':
          self.__dict__[key] = None
        else:
          self.__dict__[key] = val

      else:
        if not line.startswith('#'):
          self.description += line + '\n'

    # Clean up the description of trailing and leading whitespace.
    self.description = self.description.strip(u' \t\r\f\v\n')

    if self.description == '':
      raise WorklogValidationError('Missing worklog body.')

    if self.poster:
      try:
        self.poster = emailaddress.EmailAddress(self.poster)
      except emailaddress.EmailValidationError, e:
        raise WorklogValidationError('Poster is not a valid email address.')
    else:
      raise WorklogValidationError('Missing poster email address.')


# Make sure that when we emit stuff that the worklog shows up properly without
# extra annoying tags.
yaml.add_path_resolver(u'!worklog', (u'worklog', [list, False]))
