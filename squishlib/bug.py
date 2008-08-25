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
import cStringIO

import yaml

import emailaddress
import worklog


STATES = [
  'open',
  'reproducible',
  'in-progress',
  'duplicate',
  'invalid',
  'non-reproducible',
  'fixed',
  'wont-fix'
  ]

BUG_PATTERN = re.compile(ur'^[a-fA-F0-9*?]+$')


class BugValidationError(Exception):
  '''
  An error thrown when a bug does not validate.
  '''

  pass


class Bug(yaml.YAMLObject):
  '''
  A single bug.
  '''

  yaml_tag = u'!bug'

  _nonemptyFields = [
    'summary',
    'description',
    'reporter'
    ]

  _separatorPattern = re.compile(ur'^---[\w\s]+---$')
  _headerPattern    = re.compile(ur'^(\w+): (.*)$')

  def __init__(self):
    self.summary = None
    self.description = None
    self.reporter = None
    self.assignee = None
    self.version = None
    self.priority = None
    self.tags = []
    self.cc = []
    self.worklog = []
    self.duplicate = None

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

    print 'Reporter: %s'  % self._varOrBlank(self.reporter)
    print 'CC: %s'        % self._varOrBlank(self.cc)
    print 'Version: %s'   % self._varOrBlank(self.version)
    print 'Priority: %s'  % self._varOrBlank(self.priority)
    print 'Tags: %s'      % self._varOrBlank(self.tags)
    print 'Summary: %s'   % self._varOrBlank(self.summary)
    print '---problem description follows this line---'
    print '%s\n' % self._varOrBlank(self.description)
    print '# Describe the bug and the steps you took to cause the it here.'
    print '#'
    print '# Lines beginning with hash marks (like these) are ignored and will'
    print '# not be included in the description of the bug.'
    print '#'
    print '# Fields that are absolutely required are Reporter, Summary, and the'
    print '# problem description. If any one of those three fields are left'
    print '# empty, the bug report will be aborted.'
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
      self.description = None

    # Convert the strings we just ingested to their proper values.
    self._convertValuesToTypes()

    # Verify we have a valid bug
    self.validate()

  def _convertValuesToTypes(self):
    '''
    Convert all simple types stored in this object to more complex
    ones. Specifically, this one just converts email addresses and lists for cc
    and reporter into EmailAddress objects.
    '''

    # First, convert all email strings to EmailAddresses
    if self.reporter:
      self.reporter = emailaddress.EmailAddress(self.reporter)

    if self.assignee:
      self.assignee = emailaddress.EmailAddress(self.assignee)

    if self.cc:
      if ', ' in self.cc:
        temp = self.cc.split(',')
        temp = map(lambda s: emailaddress.EmailAddress(s), temp)
      else:
        temp = [ self.cc ]

      self.cc = temp

  def validate(self):
    '''
    Validate that the appropriate fields for the bug have been filled out.
    '''

    for field in self._nonemptyFields:
      if (not self.__dict__.has_key(field)
          or not self.__dict__[field]):
        raise BugValidationError('%s is not set to a value' % field)


def loadBugFromFile(filename):
  '''
  Load a yaml stream from filename and de-serialize into a proper Bug instance.
  '''

  stream = file(filename, 'r')
  result = yaml.load(stream)
  stream.close()

  if not result or not isinstance(result, Bug):
    raise BugValidationError('invalid or corrupt bug')

  result.validate()

  return result

def dumpBugToFile(bugreport, filename):
  '''
  Dump a yaml stream from a bugreport to the filename provided.
  '''

  stream = file(filename, 'w')
  yaml.dump(bugreport, stream, default_flow_style=False)
  stream.close()
