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
import yaml
import datetime

import emailaddress


class Worklog(yaml.YAMLObject):
  '''
  A single worklog entry. Bugs typically have zero or more of these.
  '''

  yaml_tag = '!worklog'

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


# Make sure that when we emit stuff that the worklog shows up properly without
# extra annoying tags.

yaml.add_path_resolver(u'!worklog', (u'worklog', [list, False]))
