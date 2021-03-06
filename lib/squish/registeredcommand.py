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

import yaml


commands = {}


class RegisteredCommand(type):
  '''
  Metaclass that handles registration with the __init__ varaible 'commands' so
  that proper command line parsing can happen.
  '''

  _required_attributes = [
    'command_name',
    'synopsis',
    'usage'
    ]

  def __init__(mcs, name, bases, dct):
    type.__init__(mcs, name, bases, dct)

    # Verify that the required attributes are set.
    for attr in RegisteredCommand._required_attributes:
      if not dct.has_key(attr):
        for base in bases:
          if (hasattr(base, '__metaclass__') and
              base.__metaclass__ == RegisteredCommand):
            raise NameError, ('Subclasses of %s must have a %s '
                              'attribute defined.') % [base.__name__, attr]

      # If we passed, add the new command to the registered commands list.
      commands[dct['command_name']] = mcs
