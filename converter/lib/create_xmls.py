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
import textwrap
import os
from collections import namedtuple
from ossie import version
from ossie.parsers import scd, spd, prf
from redhawk.packagegen.resourcePackage import ResourcePackage
from redhawk.packagegen.softPackage import SoftPackage

from redhawk.codegen.jinja.python.component.gr_flowgraph.mapping import FG_KEY_FILE, FG_KEY_CLASS_NAME

SInterface = namedtuple("SInterface", "name id inherits")

BLOCK_TO_BULKIO_MAP = {
    "float":    "dataFloat",
    "complex":  "dataFloat",
    "int":      "dataLong",
    "short":    "dataShort",
    "byte":     "dataOctet"
}

# ##############################################################################
# Optionally, this method will manually add the interfaces, inheritedInterfaces,
# and supported interfaces that are present within generated SCD files from
# the REDHAWK IDE (this code is located between the "~" signs). This method
# also adds the provides and usesPort "attributes" to the current SCD file.
# ##############################################################################
def formatSCD(rp, ports):

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
        
    for interface in all_interfaces.get_interface():
        if "Resource" in interface.name:
            interface.add_inheritsinterface(scd.inheritsInterface("IDL:CF/Logging:1.0"))

    rp.scd.set_componentfeatures(sup_interfaces)

    ports_scd = rp.scd.componentfeatures.get_ports()
    if ports_scd is None:
        ports_scd = scd.ports()
    
    all_data_types = set()
    for port in ports:
        data_type = BLOCK_TO_BULKIO_MAP.get(port.type)
        
        if data_type is None:
            raise Exception("Unknown source block data type: %s" % port.type)

        repid = "IDL:BULKIO/%s:1.0" % data_type

        if port.direction.endswith('source'):
            all_data_types.add((data_type, 'Provides'))
            ports_scd.add_provides(scd.provides(
                providesname=port.name,
                repid=repid))
        elif port.direction.endswith('sink'):
            all_data_types.add((data_type, 'Uses'))
            ports_scd.add_uses(scd.uses(
                usesname=port.name,
                repid=repid))
        else:
            raise Exception("Unknown block port direction: %s" % port.type)
    
    for dt in all_data_types:
        if dt[1] == "Provides":
            all_interfaces.add_interface(scd.interface(dt[0], "IDL:BULKIO/{0}:1.0".format(dt[0]), [
                scd.inheritsInterface("IDL:BULKIO/{0}PortStatisticsProvider:1.0".format(dt[1])), 
                scd.inheritsInterface("IDL:BULKIO/updateSRI:1.0")]))
        else:
            all_interfaces.add_interface(scd.interface(dt[0], "IDL:BULKIO/{0}:1.0".format(dt[0])))
    
    rp.scd.set_interfaces(all_interfaces)
    rp.scd.componentfeatures.set_ports(ports_scd)

# ##############################################################################
# This method creates a simpleProperty object for each variable block that
# has been determined to be a property (referenced by another variable or block)
# and formats the name of the property in a required way.
# ##############################################################################
def formatPRF(rp, props, docker_image, docker_volumes):

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

    def docker_execparam(name, value, description):
        return prf.simple(
            id_=name,
            value=value,
            type_='string',
            commandline='true',
            kind=[prf.kind(kindtype='property')],
            action=prf.action(type_='external'),
            description=description)

    # If docker_image is defined, add an exec param __DOCKER_IMAGE__
    if docker_image:
        rp.prf.add_simple(docker_execparam(
            name='__DOCKER_IMAGE__',
            value=docker_image,
            description='Docker image containing this Component\'s environment'))

    # If docker_volumes is defined, add an exec param __DOCKER_ARGS__
    # for "--volumes-from docker_volumes"
    if docker_volumes:
        vols = ''
        for vol in docker_volumes:
            vols += '--volumes-from %s ' % vol
        rp.prf.add_simple(docker_execparam(
            name='__DOCKER_ARGS__',
            value=vols,
            description='Docker \'run\' arguments for this Component\'s container'))

# ##############################################################################
# This section is where we manipulate certain properties of the SPD
# file before it gets generated, so that it meets the requirements that
# we have set out for SPD files. More specifically, a 32 digit alpha-numeric
# sequence is generated so that the component can be uniquely identified and a
# description is generated to tell about the file's date/time of creation and
# show the GRC file's content MD5sum value.
# ##############################################################################
def formatSPD(rp, grc_input, parsed_grc, docker_image, docker_volumes):
    new_id = "DCE:" + str(uuid.uuid4())
    rp.spd.set_id(new_id)
    rp.spd.set_type(version.__version__)
    rp.spd.propertyfile.set_type("PRF")

    md5sum = subprocess.check_output(["md5sum", grc_input])
    m = md5sum.split(" ")[0]

    # BTG: Embedding the generated flowgraph python file name and class
    # into the description of the implementation.  I'm not excited about
    # this, but I saw no other way to get this meta into the template 
    # generator/mapper construct later.
    script_name = os.path.basename(__file__)
    create_time = time.strftime("%H:%M:%S")
    create_date = time.strftime("%d/%m/%Y")
    description = textwrap.dedent("""\
        AUTO GENERATED by \"{0}\"
            Time:                      {1}
            Date:                      {2}
        MD5 hexdigest of provided GRC: {3}

        {4}:{5}
        {6}:{7}
        """.format(script_name, create_time, create_date, m,
            FG_KEY_FILE, parsed_grc.python_file_name,
            FG_KEY_CLASS_NAME, parsed_grc.python_class_name))

    rp.spd.implementation[0].set_description(description)

    # Add dependencies for docker_image and docker_volumes if specified.
    deps = []
    if docker_image:
        deps.append(spd.dependency(
            'allocation',
            propertyref=spd.propertyRef(
                'DCE:c38d28a6-351d-4aa4-a9ba-3cea51966838',
                docker_image)
            ))

    if docker_volumes:
        for vol in docker_volumes:
            deps.append(spd.dependency(
                'allocation',
                propertyref=spd.propertyRef(
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
def main(name, output_dir, parsed_grc, grc_input, docker_image, docker_volumes):
    implementation = "python"
    generator = "python.component.gr_flowgraph"

    rp = ResourcePackage(name, implementation, output_dir, generator)

    formatSPD(
        rp=rp,
        grc_input=grc_input,
        parsed_grc=parsed_grc,
        docker_image=docker_image,
        docker_volumes=docker_volumes)
    formatPRF(
        rp=rp,
        props=parsed_grc.properties_array,
        docker_image=docker_image,
        docker_volumes=docker_volumes)
    formatSCD(
        rp=rp,
        ports=parsed_grc.ports_array)

    rp.writeXML()

    return rp
