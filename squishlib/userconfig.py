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
import pwd
import posix
import socket

import yaml


class UserConfig(yaml.YAMLObject):
  '''
  Yaml class to handle serialization of the public configuration of the bug
  tracker. See UserConfig for user-specific private settings.
  '''

  yaml_tag = u'!UserConfig'

  def __init__(self):
    self.email = self.getEmailAddress()

  def getUsername(self):
    if os.environ.has_key('SQUISH_USER'):
      return os.environ['SQUISH_USER']
    elif os.environ.has_key('USER'):
      return os.environ['USER']
    else:
      uid = posix.getuid()
      return pwd.getpwuid(uid)[0]     # first field is username

    return None

  def getFullname(self):
    if os.environ.has_key('SQUISH_NAME'):
      return os.environ['SQUISH_NAME']
    else:
      uid = posix.getuid()
      return pwd.getpwuid(uid)[4]     # fifth field is fullname

    return None

  def getEmailAddress(self):
    if os.environ.has_key('SQUISH_EMAIL'):
      email = os.environ['SQUISH_EMAIL']
    elif os.environ.has_key('EMAIL'):
      email = os.environ['EMAIL']

    hostname = socket.gethostname()
    return '"%s" <%s@%s>' % (self.getFullname(),
                             self.getUsername(),
                             hostname)
