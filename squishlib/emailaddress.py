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
import sys

import yaml


EMAIL_PATTERN = re.compile(
  (ur'(?:"(?P<comment>.+)")?'           # "comment"
   ur'[ \t]*'                           # whitespace
   ur'(?P<angle><)?'                    # <
   ur'(?P<username>[\w.+-]+)@'          # username@
   ur'(?P<domain>[\w-]+(?:\.[\w-]+)+)'  # domain.com
   ur'(?(angle)>)'))                    # >


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

  @classmethod
  def to_yaml(cls, dumper, data):
    return dumper.represent_scalar(u'!emailaddress', u'%s' % str(data))

  @classmethod
  def from_yaml(cls, loader, node):
    value = loader.construct_scalar(node)
    return EmailAddress(value)

  def _parseEmailAddress(self, address):
    # Clean up any trailing and leading whitespace.
    address.strip()

    match = EMAIL_PATTERN.match(address)

    if match == None:
      raise EmailValidationError('Address %s is not a valid email address.'
                                 % address)

    if len(match.groups()) < 3:    # Need username, domain, and the <
      raise EmailValidationError('Address %s is not a valid email address.'
                                 % address)

    if (not match.group('username')
        or not match.group('domain')):
      raise EmailValidationError('Address %s is not a valid email address.'
                                 % address)

    self.comment = match.group('comment')
    self.user    = match.group('username')
    self.domain  = match.group('domain')

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
    return str(self)

  def __eq__(self, other):
    if isinstance(other, EmailAddress):
      if (other.user == self.user and
          other.domain == self.domain):
        return True
      return False

  def __ne__(self, other):
    if isinstance(other, EmailAddress):
      if (other.user != self.user and
          other.domain != self.domain):
        return True
      return False

# Make sure that when we emit stuff taht the email addresses show up properly
# without extra annoying tags.

yaml.add_implicit_resolver(u'!emailaddress', EMAIL_PATTERN)
