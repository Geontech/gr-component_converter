#!/usr/bin/env python2

##################################################
# File: run.py
# Author: Chris Conover
# Description: "Schedules" nescessary operations
#              for gr-redhawk templating
# Created: Wed July 13 10:00:00 2017
##################################################

import create_xmls as cx
import jinja_file_edits as jfe
import os
import re
import subprocess
import sys
from python_formatter import PythonFormatter
from xml_parsing import XMLParsing

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
def main():

    # ##########################################################################
    # This section is used to perform checks on user provided command-line
    # inputs to make sure that they exist, and that the passed file is of the
    # correct type. If not, the program exits with an appropriate message.
    # ##########################################################################

    grc_input = os.path.abspath(sys.argv[1])

    # Determine if the user provided an output_dir arg, if not, default to "."
    if len(sys.argv) == 3:
        output_dir = os.path.abspath(sys.argv[2])
    else:
        output_dir = os.path.abspath("./")

    grc_exists = os.path.exists(grc_input)
    output_dir_exists = os.path.isdir(output_dir)

    if not grc_exists:
        sys.exit("Error: Provided file does not exist. Exiting.")
    elif not output_dir_exists:
        sys.exit("Error: Provided output directory does not exist. Exiting.")

    # Extract only the name of the GRC file from the entire absolute path
    temp = grc_input.rfind("/")
    grc_name = grc_input[temp+1:]

    if ".grc" not in grc_name:
        sys.exit("A GNU Radio \".grc\" file was expected, but was not provided."
            + " Exiting.")


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

    subprocess.call(["./grc_to_py.sh", grc_input, parsed_grc.python_file_name,
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
    # old_generator = "python.component.pull"

    respkg = cx.main(trimmed_grc_name, "python", output_dir,
        generator, parsed_grc.properties_array,
        parsed_grc.source_types, parsed_grc.sink_types, grc_input, py_path)

    jfe.main(parsed_grc.python_file_name, trimmed_grc_name, parsed_grc.properties_array, respkg["pd"])

    respkg["rp"].callCodegen(force=True) #Generates remaining nescessary files

    jfe.modify_make_am_ide(respkg["rp"].autotoolsDir, parsed_grc.python_file_name)

    subprocess.call(["mv", py_path, respkg["rp"].autotoolsDir])

if __name__ == '__main__':
    main()
