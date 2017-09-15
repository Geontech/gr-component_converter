# This file is protected by Copyright. Please refer to the COPYRIGHT file
# distributed with this source distribution.
#
# This file is part of Geon's GNURadio-REDHAWK.
#
# GNURadio-REDHAWK is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# GNURadio-REDHAWK is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.
#

.PHONY: install

# Location of the python component template(s)
OSSIEHOME := $(shell bash -c ". /etc/profile; env | grep -Po '(?<=OSSIEHOME=).+'")
PY_COMP_DIR := $(OSSIEHOME)/lib/python/redhawk/codegen/jinja/python/component

# Installation location
TARGET_NAME := gr_flowgraph
INSTALL_TARGET := $(PY_COMP_DIR)/$(TARGET_NAME)

install: $(INSTALL_TARGET)

$(INSTALL_TARGET):
	cp -r $(TARGET_NAME) $(INSTALL_TARGET)

uninstall:
	rm -rf $(INSTALL_TARGET)