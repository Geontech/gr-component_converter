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
from redhawk.codegen.jinja.python.component.pull.mapping import PullComponentMapper
from redhawk.codegen.jinja.python.ports import PythonPortMapper
from ossie.parsers import spd

FG_KEY_FILE =       'flowgraph.file'
FG_KEY_CLASS_NAME = 'flowgraph.class_name'

class GrFlowGraphComponentMapper(PullComponentMapper):
    def _mapComponent(self, softpkg):
        # Defer most mapping to base class
        pycomp = super(GrFlowGraphComponentMapper,self)._mapComponent(softpkg)

        # Parse the component's description for the flow graph package and class
        # names.  There's only one implementation from our converter tooling.
        the_spd = spd.parse(softpkg.spdFile())
        the_impl = the_spd.get_implementation()[0]

        impdesc = the_impl.description
        fg_file_name  = re.search(FG_KEY_FILE + ':(.+)', impdesc).group(1)
        fg_class_name = re.search(FG_KEY_CLASS_NAME + ':(.+)', impdesc).group(1)
        pycomp['flowgraph'] = {
            'file':       fg_file_name,
            'class_name': fg_class_name
        }

        # Search the dependencies for the Docker image dependency
        fg_docker_image = None    
        for dep in the_impl.get_dependency():
            if dep.type_ == 'allocation' and dep.propertyref:
                if dep.propertyref.refid == 'DCE:c38d28a6-351d-4aa4-a9ba-3cea51966838':
                    fg_docker_image = dep.propertyref.value
        pycomp['flowgraph'].update({'docker_image': fg_docker_image})

        return pycomp

# Port names within the flow graph are snake case and do not have
# numbers in them.
def fg_snake_case_port(name):
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('_[0-9]+', '', name).lower()

class GrFlowGraphPythonPortMapper(PythonPortMapper):
    def _mapPort(self, port, generator):
        pyport = PythonPortMapper._mapPort(self, port, generator)
        fg_member = port.description()
        fg_name = fg_snake_case_port(port.name())

        pyport['flowgraph'] = {
            'member': fg_member,
            'name':   fg_name
        }
        return pyport