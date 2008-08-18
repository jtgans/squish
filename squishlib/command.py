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
import os.path
import sys
import optparse

from . import progName
from . import __version__

from debuggable import Debuggable
from registeredcommand import RegisteredCommand
from registeredcommand import commands


class Command(Debuggable):
  '''
  Base class for all squish commands. Contains methods and helpers that are
  common to all commands.
  '''

  __metaclass__ = RegisteredCommand

  command_name = ''
  synopsis     = ''
  usage        = ''

  _parser = None
  _args   = None
  _flags  = None

  def __init__(self):
    # Generate our default values for the options
    pager_cmd = (os.environ.has_key('PAGER') and os.environ['PAGER']) or ''

    self._parser = optparse.OptionParser(usage='',
                                         version=self._getVersionString())

    self._parser.add_option('--pager', dest='pager_cmd',
                            action='store', default=pager_cmd,
                            help=('The path to the pager command to use. '
                                  'Defaults to the environment variable PAGER '
                                  'if set. If PAGER is not set, or the '
                                  'controlling terminal is not a tty, the '
                                  'pager will not be used.'))

    self._parser.add_option('--no-pager', dest='use_pager',
                            action='store_false', default=True,
                            help='Don\'t use the pager.')

    self._parser.add_option('--debug', dest='debug',
                            action='store_true', default=False,
                            help='Turn on debugging information.')

    # Let our subclasses alter the opt parser if needed.
    self._setupOptParse()

    # Go!
    (self._flags, self._args) = self._parser.parse_args()

    # Do some final cleanup with the options to make sure they're sane.
    if self._flags.use_pager:
      if (not sys.stdout.isatty() or
          not os.path.exists(self._flags.pager_cmd)):
        self._flags.use_pager = False

    self._debug_mode = self._flags.debug
    self._setName(self.command_name)

  def _getVersionString(self):
    version = '.'.join(map(str, __version__))
    return '%s %s' % (progName, version)

  def generateHelp(self):
    '''
    Abstract method to generate the help string for this command.
    '''

    raise NotImplementedError, ('generateHelp must be implemented by '
                                'subclasses of Command')

  def _setupOptParse(self):
    '''
    Abstract method to allow subclasses to alter the opt parser.
    '''

    raise NotImplementedError, ('_setupOptParse must be implemented by '
                                'subclasses of Command')


# Make sure the abstract Command class doesn't show up in the registered command
# list.
del commands['']