#% set className = component.userclass.name
#% set baseClass = component.baseclass.name
#% set artifactType = component.artifacttype
#!/usr/bin/env python
#
#% block license
#% endblock
#
# AUTO-GENERATED
#
# Source: ${component.profile.spd}
#{% if component is device %}
from ossie.device import start_device
#{% else %}
from ossie.resource import start_component
#{% endif %}
from ossie.cf import CF__POA
import logging
from subprocess import call
import sys, os
from omniORB import CORBA
import CosNaming
import time

from ${baseClass} import *
from ossie.utils import redhawk

#{% block topblockimport %}
#{% endblock %}

class ${className}(${baseClass}):

    def __init__(self, identifier, execparams):
        naming_context_ior = execparams["NAMING_CONTEXT_IOR"]
        corba_namespace_name = execparams["NAME_BINDING"]

        # Get the top block
        self.tb = top_block(naming_context_ior, corba_namespace_name)
        time.sleep(2)

        # Flags for started and locked states
        self.tb_is_started = False

        # Base class init
        ${baseClass}.__init__(self, identifier, execparams)

    #{% block addpropertychangelisteners %}
    #{% endblock %}

    #{% block propertychanged %}
    #{% endblock %}

    def tb_start(self):
        if not self.tb_is_started:
            self.tb.start()
            self.tb_is_started = True

    def tb_stop(self):
        if self.tb_is_started:
            self.tb.stop()
            self.tb.wait()
            self.tb_is_started = False

    def start(self):
        self.tb_start()
        #{% block start %}
        #{% endblock %}

    def stop(self):
        self.tb_stop()
        #{% block stop %}
        #{% endblock %}

    def getPort(self, name):
        #{% block getport %}
        #{% endblock %}

    def process(self):
        return NORMAL

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    logging.debug("Starting Component")
    #{% block startcomponent %}
    #{% endblock %}
