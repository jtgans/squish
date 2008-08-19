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


EMAIL_PATTERN = re.compile(
  (ur'("[^"]+")? ?'
   ur'<?([a-zA-Z0-9.+-]+)@'
   ur'([a-zA-Z0-9.+-]+)>?'))


class EmailValidationError(Exception):
  '''
  An exception for when an email address does not validate.
  '''

  pass


class EmailAddress(yaml.YAMLObject):
  '''
  An email address of the typical RFC form:
    "Comment (full name usually here)" <user@host>
  '''

  yaml_tag = u'!emailaddress'

  _nonemptyFields = [
    'user',
    'domain'
    ]

  def __init__(self, user_or_email_address, domain=None, comment=None):
    if domain == None:
      self._parseEmailAddress(user_or_email_address)
    else:
      self.user = user_or_email_address
      self.domain = domain
      self.comment = comment

  def _parseEmailAddress(self, address):
    match = EMAIL_PATTERN.match(address)

    if match == None:
      raise EmailValidationError('Address %s is not a valid email address.'
                                 % address)

    groups = match.groups()

    if ((len(groups) < 2)
        or not groups[1]
        or not groups[2]):
      raise EmailValidationError('Address %s is not a valid email address.'
                                 % address)

    self.comment = groups[0]
    self.user    = groups[1]
    self.domain  = groups[2]

    self.validate()

  def validate(self):
    for field in self._nonemptyFields:
      if (not self.__dict__.has_key(field)
          or not self.__dict__[field]):
        raise EmailValidationError('Address is missing the %s field.'
                                   % field)

  def __str__(self):
    if self.comment:
      return '"%s" <%s@%s>' % (self.comment,
                               self.user,
                               self.domain)
    else:
      return '<%s@%s>' % (self.user, self.domain)

  def __repr__(self):
    return 'EmailAddress(\'%s\')' % str(self)


# Make sure that when we emit stuff taht the email addresses show up properly
# without extra annoying tags.
yaml.add_implicit_resolver(u'!emailaddress', EMAIL_PATTERN)
