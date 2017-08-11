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
from ossie.cf import CF_POA
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

    def constructor(self):

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

#{#

#     def constructor(self):
# #{% if 'FrontendTuner' in component.implements %}
#         self.setNumChannels(1, "RX_DIGITIZER");
# #{% endif %}
#
# #{% block updateUsageState %}
# #{% if component is device %}
#     def updateUsageState(self):
#         """
#         This is called automatically after allocateCapacity or deallocateCapacity are called.
#         Your implementation should determine the current state of the device:
#            self._usageState = CF.Device.IDLE   # not in use
#            self._usageState = CF.Device.ACTIVE # in use, with capacity remaining for allocation
#            self._usageState = CF.Device.BUSY   # in use, with no capacity remaining for allocation
#         """
#         return NOOP
#
# #{% endif %}
# #{% endblock %}
#     def process(self):
#         """
#         Basic functionality:
#
#             The process method should process a single "chunk" of data and then return. This method
#             will be called from the processing thread again, and again, and again until it returns
#             FINISH or stop() is called on the ${artifactType}.  If no work is performed, then return NOOP.
#
#         StreamSRI:
#             To create a StreamSRI object, use the following code (this generates a normalized SRI that does not flush the queue when full):
#                 sri = bulkio.sri.create("my_stream_id")
# #{% if component is device %}
# #{% if 'FrontendTuner' in component.implements %}
#
#             To create a StreamSRI object based on tuner status structure index 'idx' and collector center frequency of 100:
#                 sri = frontend.sri.create("my_stream_id", self.frontend_tuner_status[idx], self._id, collector_frequency=100)
# #{% endif %}
# #{% endif %}
#
#         PrecisionUTCTime:
#             To create a PrecisionUTCTime object, use the following code:
#                 tstamp = bulkio.timestamp.now()
#
#         Ports:
#
#             Each port instance is accessed through members of the following form: self.port_<PORT NAME>
#
#             Data is obtained in the process function through the getPacket call (BULKIO only) on a
#             provides port member instance. The optional argument is a timeout value, in seconds.
#             A zero value is non-blocking, while a negative value is blocking. Constants have been
#             defined for these values, bulkio.const.BLOCKING and bulkio.const.NON_BLOCKING. If no
#             timeout is given, it defaults to non-blocking.
#
#             The return value is a named tuple with the following fields:
#                 - dataBuffer
#                 - T
#                 - EOS
#                 - streamID
#                 - SRI
#                 - sriChanged
#                 - inputQueueFlushed
#             If no data is available due to a timeout, all fields are None.
#
#             To send data, call the appropriate function in the port directly. In the case of BULKIO,
#             convenience functions have been added in the port classes that aid in output.
#
#             Interactions with non-BULKIO ports are left up to the ${artifactType} developer's discretion.
#
#         Messages:
#
#             To receive a message, you need (1) an input port of type MessageEvent, (2) a message prototype described
#             as a structure property of kind message, (3) a callback to service the message, and (4) to register the callback
#             with the input port.
#
#             Assuming a property of type message is declared called "my_msg", an input port called "msg_input" is declared of
#             type MessageEvent, create the following code:
#
#             def msg_callback(self, msg_id, msg_value):
#                 print msg_id, msg_value
#
#             Register the message callback onto the input port with the following form:
#             self.port_input.registerMessage("my_msg", ${className}.MyMsg, self.msg_callback)
#
#             To send a message, you need to (1) create a message structure, and (2) send the message over the port.
#
#             Assuming a property of type message is declared called "my_msg", an output port called "msg_output" is declared of
#             type MessageEvent, create the following code:
#
#             msg_out = ${className}.MyMsg()
#             this.port_msg_output.sendMessage(msg_out)
#
# #{% if component is device %}
#     Accessing the Application and Domain Manager:
#
#         Both the Application hosting this Component and the Domain Manager hosting
#         the Application are available to the Component.
#
#         To access the Domain Manager:
#             dommgr = self.getDomainManager().getRef();
#         To access the Application:
#             app = self.getApplication().getRef();
# #{% else %}
#     Accessing the Device Manager and Domain Manager:
#
#         Both the Device Manager hosting this Device and the Domain Manager hosting
#         the Device Manager are available to the Device.
#
#         To access the Domain Manager:
#             dommgr = self.getDomainManager().getRef();
#         To access the Device Manager:
#             devmgr = self.getDeviceManager().getRef();
# #{% endif %}
#         Properties:
#
#             Properties are accessed directly as member variables. If the property name is baudRate,
#             then accessing it (for reading or writing) is achieved in the following way: self.baudRate.
#
#             To implement a change callback notification for a property, create a callback function with the following form:
#
#             def mycallback(self, id, old_value, new_value):
#                 pass
#
#             where id is the property id, old_value is the previous value, and new_value is the updated value.
#
#             The callback is then registered on the component as:
#             self.addPropertyChangeListener('baudRate', self.mycallback)
#
# #{% if component is device %}
#         Allocation:
#
#             Allocation callbacks are available to customize a Device's response to an allocation request.
#             Callback allocation/deallocation functions are registered using the setAllocationImpl function,
#             usually in the initialize() function
#             For example, allocation property "my_alloc" can be registered with allocation function
#             my_alloc_fn and deallocation function my_dealloc_fn as follows:
#
#             self.setAllocationImpl("my_alloc", self.my_alloc_fn, self.my_dealloc_fn)
#
#             def my_alloc_fn(self, value):
#                 # perform logic
#                 return True # successful allocation
#
#             def my_dealloc_fn(self, value):
#                 # perform logic
#                 pass
# #{% endif %}
#
#         Example:
#
#             # This example assumes that the ${artifactType} has two ports:
#             #   - A provides (input) port of type bulkio.InShortPort called dataShort_in
#             #   - A uses (output) port of type bulkio.OutFloatPort called dataFloat_out
#             # The mapping between the port and the class if found in the ${artifactType}
#             # base class.
#             # This example also makes use of the following Properties:
#             #   - A float value called amplitude
#             #   - A boolean called increaseAmplitude
#
#             packet = self.port_dataShort_in.getPacket()
#
#             if packet.dataBuffer is None:
#                 return NOOP
#
#             outData = range(len(packet.dataBuffer))
#             for i in range(len(packet.dataBuffer)):
#                 if self.increaseAmplitude:
#                     outData[i] = float(packet.dataBuffer[i]) * self.amplitude
#                 else:
#                     outData[i] = float(packet.dataBuffer[i])
#
#             # NOTE: You must make at least one valid pushSRI call
#             if packet.sriChanged:
#                 self.port_dataFloat_out.pushSRI(packet.SRI);
#
#             self.port_dataFloat_out.pushPacket(outData, packet.T, packet.EOS, packet.streamID)
#             return NORMAL
#
#         """
#
#         # TODO fill in your code here
#         self._log.debug("process() example log message")
#         return NOOP
#
# #{% block extensions %}
# #{% endblock %}
#
# if __name__ == '__main__':
#     logging.getLogger().setLevel(logging.INFO)
# #{% if component is device %}
#     logging.debug("Starting Device")
#     start_device(${className})
# #{% else %}
#     logging.debug("Starting Component")
#     start_component(${className})
# #{% endif %}
#}
