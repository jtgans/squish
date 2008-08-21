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
import sys
import sha
import glob
import popen2
import optparse

import yaml

from squishlib import commands
from squishlib import progName
from command import Command

import config
import bug
import worklog
import emailaddress


class ReportCommand(Command):
  '''
  Command to report a new bug.
  '''

  command_name = 'report'
  synopsis     = 'Report a new bug.'
  usage        = 'report [<options>]'

  def __init__(self):
    Command.__init__(self)

  def _setupOptParse(self):
    pass

  def runCommand(self):
    # Prepare a new bug report
    bugreport = bug.Bug()
    bugreport.reporter = self._userConfig.email

    if self._config.add_to_cc:
      bugreport.cc.append(self._config.add_to_cc)

    template = bugreport.generateReportTemplate()

    # Let the user and the scripts have at the template
    report = self.runScripts('pre', template)
    report = self.spawnUserEditor(report, 'bugreport.txt')
    report = self.runScripts('post', report)

    try:
      bugreport.parseReportTemplate(report)
    except bug.BugValidationError, e:
      sys.stderr.write('Bug report validation error: %s\n' % str(e))
      sys.stderr.write('bugreport.txt left behind.\n')
      sys.exit(1)

    # We have a valid bug report now. Dump it to a string so we can generate the
    # sha-1 filename and dump it to the bugreport file.

    yamldump = yaml.dump(bugreport, default_flow_style=False)
    filename = sha.new(yamldump).hexdigest()

    try:
      bug.dumpBugToFile(bugreport, self._siteDir + '/open/' + filename)
    except OSError, e:
      sys.stderr.write('Unable to open %s for writing: %s\n'
                       % (self._siteDir + '/open/' + filename,
                          str(e)))
      sys.stderr.write('bugreport.txt left behind.\n')
      sys.exit(1)

    # Clean up after ourselves.

    try:
      os.unlink('bugreport.txt')
    except OSError, e:
      sys.stderr.write('Unable to unlink bugreport.txt: %s\n' % str(e))
      sys.stderr.write('Non-fatal, but you\'ll need to unlink it if you want\n')
      sys.stderr.write('to report another bug.\n')

    print 'Bug %s created.' % filename
    return 0

  def runScripts(self, kind, template):
    if kind == 'pre':
      scripts = self._config.new_pre_scripts
    elif kind == 'post':
      scripts = self._config.new_post_scripts

    if self._config.new_pre_scripts:
      for script in scripts:
        try:
          (stdout, stdin) = popen2.popen4(script)

          # Write out the template and get the result
          stdin.write(template)
          stdin.close()

          template = ''.join(stdout.readlines())
          stdout.close()
        except OSError, e:
          sys.stderr.write('Unable to execute %s: %s\n' % str(e))
          sys.stderr.write('bugreport.txt left behind.\n')
          sys.exit(1)

    return template

  def generateHelp(self):
    formatters = {
      'progname': progName,
      'option_help': self._parser.format_help()
      }

    return '''
Usage: %(progname)s report [<options>]

Report a new bug.

Note that this command spawns an editor to edit the report template. If the
template is not changed from the generated report, the bug report will be
aborted.

%(option_help)s''' % formatters
