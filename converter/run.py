#!/usr/bin/env python2

##################################################
# File: run.py
# Author: Chris Conover
# Description: "Schedules" nescessary operations
#              for gr-redhawk templating
# Created: Wed July 13 10:00:00 2017
##################################################

import os
import re
import subprocess
import sys
import logging
from optparse import OptionParser, OptionGroup

import lib.create_xmls as cx
from lib.python_formatter import PythonFormatter
from lib.xml_parsing import XMLParsing
from lib.grc_to_py import grc_to_py

LOGGER_NAME = "GRComponentConverter"

# ##############################################################################
# Optional TODO's if Time Exists:
#
# TODO : Add option for creating the output_dir path if it does not exist.
#
# TODO: Change sys.exit to a astdError output so that the message will
#       be red and bolded.
# ##############################################################################
def main(grc_file, destination, options):
    # Get logger
    _log = logging.getLogger(LOGGER_NAME)

    # ##########################################################################
    # This section is used to perform checks on user provided command-line
    # inputs to make sure that they exist, and that the passed file is of the
    # correct type. If not, the program exits with an appropriate message.
    # ##########################################################################

    grc_input = os.path.abspath(grc_file)
    _log.debug("GRC Location: {0}".format(grc_input))

    # Determine if the user provided an output_dir arg, if not, default to "."
    output_dir = os.path.abspath(destination)
    _log.debug("Destination:  {0}".format(output_dir))

    grc_exists = os.path.exists(grc_input)
    output_dir_exists = os.path.isdir(output_dir)

    if not grc_exists:
        _log.error("Provided file does not exist.")
        sys.exit(1)
    elif not output_dir_exists:
        _log.info("Provided output directory does not exist. Attempting to create new output directory...")
        os.makedirs(output_dir)
        #sys.exit(1)

    # Extract only the name of the GRC file from the entire absolute path
    grc_name = os.path.basename(grc_input)
    (trimmed_grc_name, grc_ext) = os.path.splitext(grc_name)

    if ".grc" != grc_ext:
        _log.error("A GNU Radio \".grc\" file was expected, but was not provided.")
        sys.exit(1)

    # ##########################################################################
    # Where the tooling officially begins. This section specifically creates
    # the "parsed_grc" object which in short, extracts all useful information
    # from the user passed grc file, and gives options to create and array of
    # determined properties, and find the input/output types of ports.
    # ##########################################################################

    parsed_grc = XMLParsing(grc_input)

    # Generates output_dir/<parsed_grc.python_file_name>.py
    # which may eventually conflict with the base class file name in the 
    # Component.  We rename it here.
    grc_to_py(grc_input, output_dir)
    grc_py = 'grc_' + parsed_grc.python_file_name
    os.rename(
        os.path.join(output_dir, parsed_grc.python_file_name),
        os.path.join(output_dir, grc_py))
    parsed_grc.python_file_name = grc_py

    temp_file_name = parsed_grc.python_file_name.rstrip(".py")                  # Defining the names of two temporary files to be created by shell script
    trimmed_file_name = temp_file_name + "_trimmed"

    py_path = output_dir + "/" + parsed_grc.python_file_name
    tmp_path = output_dir + "/" + temp_file_name
    trim_path = output_dir + "/" + trimmed_file_name

    # ##########################################################################
    # Creates and appropriately formats the generated "top_block.py" file (or
    # equivalent GRC generated python file) for use at a later time.
    # ##########################################################################
    pf = PythonFormatter(py_path, tmp_path, trim_path)
    pf.format()

    # ##########################################################################
    # This section of code calls the main method of the "create_xmls.py" file
    # which in turn creates the three necessary XML files, and stores the
    # created resourcePackage object in the "respkg" variable. Then, the
    # jinja template files are created using parsed information, and codegen
    # is called on the jinja template result. Finally, there is a one line
    # modification to the created "Makefile.am.ide" file, followed by a shell
    # process that moves the "top_block.py" (or similar) file inside the
    # newly generated directory.
    # ##########################################################################
    resource_package = cx.main(
        name =          trimmed_grc_name,
        output_dir =    output_dir,
        parsed_grc =    parsed_grc,
        grc_input =     grc_input,
        docker_image =  options.docker_image,
        docker_volumes = options.docker_volumes)

    resource_package.callCodegen(force=True) #Generates remaining nescessary files

    subprocess.call(["mv", py_path, resource_package.autotoolsDir])



if __name__ == '__main__':
    # Options parsing
    parser = OptionParser()
    parser.usage = "%prog [options] GRC_FILE [DESTINATION]"
    parser.add_option(
        "-v", "--verbose",
        help="Enable verbose logging",
        dest="verbose",
        default=False,
        action="store_true")

    group = OptionGroup(parser,
        "Docker-GPP Support",
        "Note: These options will make your Component require the Docker-GPP!")
    group.add_option(
        "--docker-image",
        help="Docker Image name that will house this component",
        dest="docker_image",
        default=None)
    group.add_option(
        "--docker-volume",
        help="Docker Volume(s) required by this component (repeat if multiple)",
        dest="docker_volumes",
        action="append",
        type="string",
        default=None)
    parser.add_option_group(group)

    (options, args) = parser.parse_args()

    # Setup logging
    logging.basicConfig(format='%(name)-12s:%(levelname)-8s: %(message)s', level=logging.INFO)
    if options.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    _log = logging.getLogger(LOGGER_NAME)

    # Validate 
    if options.docker_volumes and not options.docker_image:
        _log.error("If a volume is specified, then an image must be specified.");
        sys.exit(1)

    num_args = len(args)
    if num_args == 0:
        _log.error("Must specify the location of a GRC file")
        sys.exit(1)

    grc_file = args[0]
    destination = './'
    if num_args == 2:
        destination = args[1]

    main(grc_file, destination, options)
