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


class Config(yaml.YAMLObject):
  '''
  Yaml class to handle serialization of the public configuration of the bug
  tracker. See UserConfig for user-specific private settings.
  '''

  yaml_tag = u'!Config'

  def __init__(self):
    self.new_pre_scripts = None
    self.new_post_scripts = None
    self.add_to_cc = None

    self.priorities = [
      'feature-request',
      'minor',
      'major',
      'severe',
      'blocker',
      'crash' ]

    self.email_on = [ 'all' ]
