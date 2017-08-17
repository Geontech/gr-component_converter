##################################################
# File: create_xmls.py
# Author: Chris Conover
# Description: Creates three required XML files
#              for REDHAWK Componenet deployment.
# Created: Wed July 26 10:00:00 2017
##################################################

import hashlib
import subprocess
import time
import uuid
from collections import namedtuple
from ossie import version
from ossie.parsers import scd
from redhawk.packagegen.resourcePackage import ResourcePackage
from redhawk.packagegen.softPackage import SoftPackage

SInterface = namedtuple("SInterface", "name id inherits")

# ##############################################################################
# Optionally, this method will manually add the interfaces, inheritedInterfaces,
# and supported interfaces that are present within generated SCD files from
# the REDHAWK IDE (this code is located between the "~" signs). This method
# also adds the provides and usesPort "attributes" to the current SCD file.
# ##############################################################################
def formatSCD(rp, sources, sinks):

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    supports_list = [SInterface(name="PropertyEmitter", id="IDL:CF/PropertyEmitter:1.0", inherits=[scd.inheritsInterface("IDL:CF/PropertySet:1.0")]),
        SInterface(name="PortSet", id="IDL:CF/PortSet:1.0", inherits=[scd.inheritsInterface("IDL:CF/PortSupplier:1.0")]),
        SInterface(name="Logging", id="IDL:CF/Logging:1.0", inherits=[scd.inheritsInterface("IDL:CF/LogEventConsumer:1.0"), scd.inheritsInterface("IDL:CF/LogConfiguration:1.0")]),
        SInterface(name="LogEventConsumer", id="IDL:CF/LogEventConsumer:1.0", inherits=None),
        SInterface(name="LogConfiguration", id="IDL:CF/LogConfiguration:1.0", inherits=None)]

    all_interfaces = rp.scd.get_interfaces()
    sup_interfaces = rp.scd.get_componentfeatures()

    for si in supports_list:
        all_interfaces.add_interface(scd.interface(si.name, si.id, si.inherits))
        sup_interfaces.add_supportsinterface(scd.supportsInterface(si.name, si.id))

    all_interfaces.add_interface(scd.interface("dataShort", "IDL:BULKIO/dataShort:1.0", [scd.inheritsInterface("IDL:BULKIO/ProvidesPortStatisticsProvider:1.0"), scd.inheritsInterface("IDL:BULKIO/updateSRI:1.0")]))

    for interface in all_interfaces.get_interface():
        if "Resource" in interface.name:
            interface.add_inheritsinterface(scd.inheritsInterface("IDL:CF/Logging:1.0"))

    rp.scd.set_interfaces(all_interfaces)
    rp.scd.set_componentfeatures(sup_interfaces)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    ports_data = []

    for idx, block in enumerate(sources):

        data_type = "data" + str(block.type).capitalize()

        if len(sources) > 1:
            new_name = data_type + "_%s_in" % (idx + 1)
        else:
            new_name = data_type + "_in"

        ports_data.append((block.name, new_name))

        new_type = "IDL:BULKIO/%s:1.0" % data_type
        rp.addProvidesPort(new_name, new_type)

    for idx, block in enumerate(sinks):

        data_type = "data" + str(block.type).capitalize()

        if len(sinks) > 1:
            new_name = data_type + "_%s_out" % (idx + 1)
        else:
            new_name = data_type + "_out"

        ports_data.append((block.name, new_name))

        new_type = "IDL:BULKIO/%s:1.0" % data_type
        rp.addUsesPort(new_name, new_type)

    return ports_data

# ##############################################################################
# This method creates a simpleProperty object for each variable block that
# has been determined to be a property (referenced by another variable or block)
# and formats the name of the property in a required way.
# ##############################################################################
def formatPRF(rp, props):

    # ##########################################################################
    # I'm not sure how much of a resource difference it would make (probably
    # minimal), but if I were to redefine props[i].name to be "new_id", the
    # entire namedTuple will be recreated since it is immutable. I only mention
    # this because currently the "gr::" and "gr_" are being appended to this
    # value at two different places in this code scheme, "jinja_file_edits.py"
    # being the other.
    # ##########################################################################
    for i in range(0, len(props)):
        new_id = "gr::" + props[i].name
        new_name = "gr_" + props[i].name
        rp.addSimpleProperty(id=new_id, value=props[i].value, complex=False, type=props[i].type, kindtypes=["property"])
        rp.prf.simple[i].set_name(new_name)

# ##############################################################################
# This section is where we manipulate certain properties of the SPD
# file before it gets generated, so that it meets the requirements that
# we have set out for SPD files. More specifically, a 32 digit alpha-numeric
# sequence is generated so that the component can be uniquely identified and a
# description is generated to tell about the file's date/time of creation and
# show the GRC file's content MD5sum value.
# ##############################################################################
def formatSPD(rp, grc_input, docker_image, docker_volume):
    new_id = "DCE:" + str(uuid.uuid4())
    rp.spd.set_id(new_id)
    rp.spd.set_type(version.__version__)
    rp.spd.propertyfile.set_type("PRF")

    md5sum = subprocess.check_output(["md5sum", grc_input])
    m = md5sum.split(" ")[0]

    description = "AUTO GENERATED by \"create_xmls.py\" at " + time.strftime("%H:%M:%S") \
        + " on " + time.strftime("%d/%m/%Y") + ". MD5 hexdigest of provided GRC: " \
        + m
    rp.spd.implementation[0].set_description(description)

    # Add dependencies for docker_image and docker_volume if specified.
    deps = []
    if docker_image:
        deps.append(dependency(
            'allocation',
            propertyRef(
                'DCE:c38d28a6-351d-4aa4-a9ba-3cea51966838',
                docker_image)
            ))

    if docker_volume:
        for vol in docker_volume:
            deps.append(dependency(
                'allocation',
                propertyRef(
                    'DCE:47a581c8-e31f-4284-a3ef-6d8b98385835',
                    vol)
                ))

    # Insert all dependencies, if necessary
    for dep in deps:
        rp.spd.implementation[0].add_dependency(dep)




# ##############################################################################
# The main method simply schedules all of the property and other changes that
# must occur to the three XML file types before they are generated, so that
# these files meet our and REDHAWKS criteria for a build.
# ##############################################################################
def main(name, output_dir, prop_array, source_types, sink_types, grc_input, docker_image, docker_volume):
    implementation = "python"
    generator = "python.component.gr_flowgraph"

    rp = ResourcePackage(name, implementation, output_dir, generator)
    formatSPD(rp, grc_input, docker_image, docker_volume)
    formatPRF(rp, prop_array)
    ports_data = formatSCD(rp, source_types, sink_types)

    rp.writeXML()

    return {'rp': rp, 'pd': ports_data}
