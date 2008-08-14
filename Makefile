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

PY_MODULES     := $(wildcard lib/squish/*.py)
PY_SOURCE      := $(wildcard src/*.py)
PY_UNIT_TESTS  := $(wildcard tests/unit/*_test.py)

ifndef PYCHECKER
PYCHECKER := /usr/bin/pychecker
endif

ifndef SVN_USER
SVN_USER := $(shell echo $$USER)
endif

ifndef VERSION
VERSION := $(shell cat lib/squish/__init__.py \
				|grep __version__ \
				|sed -e 's/.*= (//' -e 's/)//' -e 's/, /./g')
endif

DIST_FILENAME := squish-$(VERSION).tar.gz

all: check test

test: unit-tests

unit-tests:
	for i in $(PY_UNIT_TESTS); do \
		PYTHONPATH="./lib" python $$i || break; \
	done

check:
	-cd lib; $(PYCHECKER) -F ../pycheckerrc squish/__init__.py; cd ..
	-$(PYCHECKER) -F pycheckerrc $(PY_SOURCE)
	-$(PYCHECKER) -F pycheckerrc $(PY_UNIT_TESTS)

fixspaces:
	sed -i -r 's/^[ ]+$$//' $(PY_MODULES) $(PY_SOURCE) $(PY_TESTS)

clean:
	find -iname \*.pyc -exec rm -f '{}' ';'
	rm -f $(DIST_FILENAME)

mrclean: clean
	find -iname \*~ -exec rm -rf '{}' ';' -prune

tag:
	svn cp https://squish.googlecode.com/svn/trunk \
           https://squish.googlecode.com/svn/tags/$(VERSION) \
           --username $(SVN_USER)

$(DIST_FILENAME):
	svn export http://squish.googlecode.com/svn/tags/$(VERSION) /tmp/squish-$(VERSION)
	tar -C /tmp/squish-$(VERSION) -zcvf $(DIST_FILENAME) .
	rm -rf /tmp/squish-$(VERSION)

dist: $(DIST_FILENAME)

.PHONY: all test unit-tests check fixspaces clean mrclean dist tag