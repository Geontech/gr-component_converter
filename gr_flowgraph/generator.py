#
# This file is protected by Copyright. Please refer to the COPYRIGHT file
# distributed with this source distribution.
#
# This file is part of GNURadio REDHAWK.
#
# GNURadio REDHAWK is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# GNURadio REDHAWK is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.
#

import re
from redhawk.codegen import utils
from redhawk.codegen.jinja.loader import CodegenLoader
from redhawk.codegen.jinja.common import ShellTemplate, AutomakeTemplate, AutoconfTemplate
from redhawk.codegen.jinja.python import PythonTemplate
from redhawk.codegen.jinja.python.properties import PythonPropertyMapper
from redhawk.codegen.jinja.python.ports import PythonPortFactory

from redhawk.codegen.jinja.python.component.pull import PullComponentGenerator

from mapping import GrFlowGraphComponentMapper, GrFlowGraphPythonPortMapper

loader = CodegenLoader(__package__,
                       {'common': 'redhawk.codegen.jinja.common',
                        'pull':   'redhawk.codegen.jinja.python.component.pull',
                        'base':   'redhawk.codegen.jinja.python.component.base'})

class DockerFileTemplate(ShellTemplate):
    pass

class GrFlowGraphComponentGenerator(PullComponentGenerator):
    def map(self, softpkg):
        component = super(PullComponentGenerator,self).map(softpkg)
        return component
        
    def loader(self, component):
        return loader

    def componentMapper(self):
        return GrFlowGraphComponentMapper()

    def propertyMapper(self):
        return PythonPropertyMapper(legacy_structs=self.legacy_structs)

    def portMapper(self):
        return GrFlowGraphPythonPortMapper()

    def portFactory(self):
        return PythonPortFactory()

    def templates(self, component):
        templates = [
            PythonTemplate('pull/resource_base.py', component['baseclass']['file']),
            PythonTemplate('resource.py', component['userclass']['file'], executable=True),
            AutoconfTemplate('pull/configure.ac'),
            AutomakeTemplate('base/Makefile.am'),
            AutomakeTemplate('Makefile.am.ide'),
            ShellTemplate('common/reconf')
        ]

        # If this is a docker-borne Component, add the template generators for it.
        if component['flowgraph']['docker_image']:
            templates += [
                DockerFileTemplate('Dockerfile',
                    filename='../Dockerfile',
                    executable=False),
                ShellTemplate('build-image.sh',
                    filename='../build-image.sh',
                    executable=True)
            ]
        return templates