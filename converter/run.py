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

import lib.create_xmls as cx
import lib.jinja_file_edits as jfe
from lib.python_formatter import PythonFormatter
from lib.xml_parsing import XMLParsing

LOGGER_NAME = "GRComponentConverter"

# ##############################################################################
# TODO: Add features for --help. For example, allow --directory flag for
#       providing a user defined output directory (OPTPARSE)
#
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
        _log.error("Provided output directory does not exist.")
        sys.exit(1)

    # Extract only the name of the GRC file from the entire absolute path
    temp = grc_input.rfind("/")
    grc_name = grc_input[temp+1:]

    if ".grc" not in grc_name:
        _log.error("A GNU Radio \".grc\" file was expected, but was not provided.")
        sys.exit(1)

    # ##########################################################################
    # Where the tooling officially begins. This section specifically creates
    # the "parsed_grc" object which in short, extracts all useful information
    # from the user passed grc file, and gives options to create and array of
    # determined properties, and find the input/output types of ports.
    # ##########################################################################

    parsed_grc = XMLParsing(grc_input)
    parsed_grc.parse()
    parsed_grc.create_properties_array()
    parsed_grc.find_inout_types()

    temp_file_name = parsed_grc.python_file_name.rstrip(".py")                  # Defining the names of two temporary files to be created by shell script
    trimmed_file_name = temp_file_name + "_trimmed"

    subprocess.call(["./lib/grc_to_py.sh", grc_input, parsed_grc.python_file_name,
        output_dir, temp_file_name, trimmed_file_name])

    py_path = output_dir + "/" + parsed_grc.python_file_name
    tmp_path = output_dir + "/" + temp_file_name
    trim_path = output_dir + "/" + trimmed_file_name

    # ##########################################################################
    # Creates and appropriately formats the generated "top_block.py" file (or
    # equivalent GRC generated python file) for use at a later time.
    # ##########################################################################
    pf = PythonFormatter(py_path, tmp_path, trim_path)
    pf.format()

    trimmed_grc_name = grc_name.split(".")[0]

    # ##########################################################################
    # This section of code calls the main method of the "create_xmls.py" file
    # which in turn creates the three necessary XML files, and stores the
    # created resourcePackage object in the "respkg" variable. Then, the
    # jinja template files are created using parsed information, and codegen
    # is called on the jinja template result. Finally, there is a one line
    # modification to the created "Makefile.am.ide" file, followed by a shell
    # process that moves the "top_block.py" (or similar) file inside the
    # newly generated directory.
    #
    # TODO: This generator variable may need to be changed depending on what the
    #       actual implementation name of that directory will become, or if it
    #       will actually be present in redhawk's "pull" template, then you can
    #       make use of the commented "old_generator" variable below.
    # ##########################################################################
    generator = "python.component.gr_flowgraph"

    respkg = cx.main(trimmed_grc_name, "python", output_dir,
        generator, parsed_grc.properties_array,
        parsed_grc.source_types, parsed_grc.sink_types, grc_input, py_path)

    jfe.main(parsed_grc.python_file_name, trimmed_grc_name, parsed_grc.properties_array, respkg["pd"])

    respkg["rp"].callCodegen(force=True) #Generates remaining nescessary files

    jfe.modify_make_am_ide(respkg["rp"].autotoolsDir, parsed_grc.python_file_name)

    subprocess.call(["mv", py_path, respkg["rp"].autotoolsDir])



if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser()
    parser.usage = "%prog [options] GRC_FILE [DESTINATION]"
    parser.add_option(
        "-v", "--verbose",
        help="Enable verbose logging",
        dest="verbose",
        default=False,
        action="store_true")
    (options, args) = parser.parse_args()

    # Setup logging
    logging.basicConfig(format='%(name)-12s:%(levelname)-8s: %(message)s', level=logging.INFO)
    if options.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    _log = logging.getLogger(LOGGER_NAME)

    num_args = len(args)
    if num_args == 0:
        _log.error("Must specify the location of a GRC file")
        sys.exit(1)

    grc_file = args[0]
    destination = './'
    if num_args == 2:
        destination = args[1]

    main(grc_file, destination, options)
