#{#
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
#}
#% extends "pull/resource.py"

#{% block extensions %}
    def __init__(self, identifier, execparams):
        naming_context_ior = execparams["NAMING_CONTEXT_IOR"]
        corba_namespace_name = execparams["NAME_BINDING"]

        # Flow Graph "top block" wrapper
        # FIXME: One day, the pull component template may have a place for 
        # imports. Until then, this will work.
#{% set fg_package = component.flowgraph.file|replace(".py","") %}
#{% set fg_class = component.flowgraph.class_name %}
        from ${ fg_package } import ${ fg_class } as top_block
        self.tb = top_block(naming_context_ior, corba_namespace_name)

        # Also not happy about this kind of wake-up delay for ORB registration
        import time
        time.sleep(2)

        # Flags for started and locked states
        self.tb_is_started = False

        # Base class init
        ${baseClass}.__init__(self, identifier, execparams)


    def start(self):
        self.tb_start()
        ${baseClass}.start(self)

    def stop(self):
        self.tb_stop()
        ${baseClass}.stop(self)

#{% if component.gr_properties|length > 0 %}
    # FIXME: ...One day.  There's no way to populate the contents of 
    # constructor() automatically, however, Python is very forgiving. 
    # So we're making a second one below the original empty one.  :-)
    def constructor(self):
#{% for prop in component.gr_properties %}
#{% set prop_member = prop.identifier|replace("::","_") %}
#{% set prop_changed = prop_member ~ "_changed" %}
        self.addPropertyChangeListener("${prop.identifier}", self.${prop_changed})
        self.${prop_changed}("${prop.identifier}", None, self.${prop_member})
#{% endfor %}

#{% for prop in component.gr_properties %}
#{% set prop_member = prop.identifier|replace("::","_") %}
#{% set prop_changed = prop_member ~ "_changed" %}
#{% set prop_tb = prop_member|replace("gr_","") %}
    def ${prop_changed}(self, id, old_value, new_value):
        self.tb.set_${prop_tb}(new_value)
        self.${prop_member} = self.tb.get_${prop_tb}()
#{% endfor %}
#{% endif %}

    def tb_start(self):
        if not self.tb_is_started:
            self.tb.start()
            self.tb_is_started = True

    def tb_stop(self):
        if self.tb_is_started:
            self.tb.stop()
            self.tb.wait()
            self.tb_is_started = False

    def getPort(self, name):
#{% for port in component.ports %}
        if name == "${port.name}":
            return self.tb.${port.flowgraph.member}.getPort("${port.flowgraph.name}")
#{% endfor %}
        return None

#{% endblock %}

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    logging.debug("Starting Component")
    #{% block startcomponent %}
    #{% endblock %}
