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

import traceback
import optparse

import yaml

import squish


class Command(object):
  '''
  Base class for all squish commands. Contains methods and helpers that are
  common to all commands.
  '''

  __metaclass__ = squish.RegisteredCommand

  _command_name = ''
  synopsis      = ''
  usage         = ''

  _optparser = None

  def __init__(self):
    self._optparser = optparse.OptionParser()


# Make sure the base command doesn't show up in the registered command list.
del squish.commands['']
