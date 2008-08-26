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
import sha
import glob
import optparse

import yaml

from . import progName
from . import __version__

from debuggable import Debuggable
from registeredcommand import RegisteredCommand
from registeredcommand import commands

import bug
import config
import userconfig


class Command(Debuggable):
  '''
  Base class for all squish commands. Contains methods and helpers that are
  common to all commands.
  '''

  __metaclass__ = RegisteredCommand

  command_name = ''
  synopsis     = ''
  usage        = ''

  # Override this to allow a command to work without a squish bug repository
  # being present.
  requireSiteConfig = True

  _parser     = None
  _args       = None
  _flags      = None

  _siteDir    = None
  _config     = None
  _userConfig = None

  def __init__(self):
    self._parseArguments()

    self._siteDir = self._findSiteDir()
    self._loadSiteConfig()
    self._loadUserConfig()

    # Do some final cleanup with the options to make sure they're sane.
    if self._flags.use_pager:
      if (not sys.stdout.isatty() or
          not os.path.exists(self._flags.pager_cmd)):
        self._flags.use_pager = False

    self._debug_mode = self._flags.debug
    self._setName(self.command_name)

  def _findSiteDir(self):
    '''
    Walk the directory tree from the current directory to the root directory,
    looking for a directory called bugs with a file in it called config.yaml.
    '''

    curpath = os.path.abspath('.')

    while curpath != '/':
      if (os.path.isdir(curpath + '/bugs') and
          os.path.isfile(curpath + '/bugs/config.yaml')):
        return curpath + '/bugs'

      curpath = os.path.abspath(curpath + '/..')

    return None

  def _loadUserConfig(self):
    '''
    Load in the user's preferences config. If none exists, just initialize to
    the default and write it out to ~/.squishrc.yaml
    '''

    homedir = os.environ['HOME']
    rcfile  = '%s/.squishrc' % homedir

    if os.path.isfile(rcfile):
      try:
        stream = file(rcfile, 'r')
        self._userConfig = yaml.load(stream)
        stream.close()
      except Exception, e:
        sys.stderr.write('Unable to read from ~/.squishrc: %s\n' % str(e))
        sys.exit(1)

    else:
      self._userConfig = userconfig.UserConfig()

      try:
        stream = file(rcfile, 'w')
        yaml.dump(self._userConfig, stream, default_flow_style=False)
        stream.close()
      except Exception, e:
        sys.stderr.write('Unable to create ~/.squishrc: %s\n' % str(e))
        sys.exit(1)

  def _loadSiteConfig(self):
    '''
    Load in the site-specific config file. Should be in self._siteDir +
    '/config.yaml'. If no config.yaml file exists, throw an error and exit.
    '''

    if self._siteDir:
      if not os.path.isfile(self._siteDir + '/config.yaml'):
        sys.stderr.write('Directory %s is not a squish bug repository.\n' %
                        self._siteDir)
        sys.exit(1)

      try:
        stream = file(self._siteDir + '/config.yaml', 'r')
        self._config = yaml.load(stream)
        stream.close()
      except Exception, e:
        sys.stderr.write('Unable to load %s/config.yaml: %s\n' % (self._siteDir,
                                                                 str(e)))
        sys.exit(1)

    elif self.requireSiteConfig:
      sys.stderr.write('Unable to find squish bug repository.\n')
      sys.exit(1)

  def _parseArguments(self):
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

    # Strip off the command name from the args -- we don't need it.
    self._args = self._args[1:]

  def spawnUserEditor(self, template, filename):
    '''
    Spawn the user's editor on a template given in a specific filename.
    '''

    # Write out the bug report template so the editor can actually hack on it.
    if not os.path.isfile(filename):
      try:
        stream = file(filename, 'w')
        stream.write(template)
        stream.close()
      except OSError, e:
        sys.stderr.write('Unable to open %s for writing: %s'
                         % (filename, str(e)))
        sys.exit(1)

    # Take the hash of the template so that we know if it's been changed we can
    # go ahead and use it for the report.
    orig_hash = sha.new(template).hexdigest()

    # Spawn the user's editor here
    os.system('%s %s' % (self._userConfig.editor, filename))

    # Read it back in
    try:
      stream = file(filename, 'r')
      report = ''.join(stream.readlines())
      stream.close()
    except OSError, e:
      sys.stderr.write('Unable to open %s for reading: %s'
                       % (filename, str(e)))
      sys.stderr.write('%s has been left behind.\n' % filename)
      sys.exit(1)

    # Generate the new hash of the report
    new_hash = sha.new(report).hexdigest()

    # Verify the hash changed
    if orig_hash == new_hash:
      sys.stderr.write('Template unchanged -- aborting.\n')
      sys.stderr.write('%s has been left behind.\n' % filename)
      sys.exit(1)

    return report

  def findBugsByNumOrPartial(self, bugnum_or_partial, states=None):
    if not bug.BUG_PATTERN.match(bugnum_or_partial):
      raise TypeError('%s is not a valid bug number or partial.'
                      % bugnum_or_partial)

    filenames = []

    if not '*' in bugnum_or_partial:
      partial = bugnum_or_partial + '*'
    else:
      partial = bugnum_or_partial

    if states == None:
      states = bug.STATES
    elif not isinstance(states, list):
      raise TypeError('states must be a list or None')

    for state in states:
      if state not in bug.STATES:
        raise TypeError('%s is not a valid state.' % state)

    for state in states:
      globbed_names = glob.glob('%s/%s/%s' % (self._siteDir, state, partial))

      for name in globbed_names:
        basename = os.path.basename(name)

        if bug.BUG_PATTERN.match(basename):
          filenames.append(name)

    return filenames

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
