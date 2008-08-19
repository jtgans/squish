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

import yaml

import emailaddress


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

  def validate(self):
    for field in self._nonemptyFields:
      if (not self.__dict__.has_key(field)
          or not self.__dict__[field]):
        raise BugValidationError()
