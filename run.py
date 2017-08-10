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
import sys
import re
import os
import subprocess
from xml_parsing import XMLParsing
from python_formatter import PythonFormatter
# from create_xmls import CreateXMLs
# from redhawk.packagegen.softPackage import SoftPackage
# from redhawk.packagegen.resourcePackage import ResourcePackage

class TemplateBuildingInformation(object):

    def __init__(self, parsed_grc_file):
        self.parsed_grc_name = parsed_grc_file.python_file_name

# ##############################################################################
# This file is passed the name of a GRC file via command line argument, which
# is then used to create an XMLParsing object. From there, the "parse()" methods
# is invoked on that object which extracts relevent information from the file
# and returns a namedTuple of data for easy iteration.
# ##############################################################################

# TODO: Investigate this link on multiple regexps: https://stackoverflow.com/questions/597476/how-to-concisely-cascade-through-multiple-regex-statements-in-python

# TODO: Add features for --help. For example, allow --directory flag for
#       providing a user defined output directory

def get_parsed_grc_name():
    return self.parsed_grc_name

def main():

    # ##########################################################################
    # This section is used to perform checks on user provided command-line
    # inputs to make sure that they exist, and that the passed file is of the
    # correct type. If not, the program exits with an appropriate message.
    #
    # TODO: Change sys.exit to a astdError output so that the message will
    #       be red and bolded.
    #
    # TODO: Add option for creating the output_dir path if it does not exist
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
    # This is where the automation/scripting for the various componenets
    # begins its execution.
    # ##########################################################################

    parsed_grc = XMLParsing(grc_input)
    parsed_grc.parse()
    parsed_grc.create_properties_array()
    parsed_grc.find_inout_types()

    # ##########################################################################
    # Create a file to output GNUBlock information for use with comparisons
    # ##########################################################################

    subprocess.call(["touch", "parsed_output.txt"])
    with open("parsed_output.txt", "w") as out_file:
        out_file.write("GNU Block Array Contents: \n")
        for block in parsed_grc.block_array:
            out_file.write(str(block) + "\n")
        out_file.write("\nProperties Array Contents: \n")
        for block in parsed_grc.properties_array:
            out_file.write(str(block) + "\n")

    # Creating the names of two temporary files to be created by shell script
    temp_file_name = parsed_grc.python_file_name.rstrip(".py")
    trimmed_file_name = temp_file_name + "_trimmed"

    subprocess.call(["./grc_to_py.sh", grc_input, parsed_grc.python_file_name,
        output_dir, temp_file_name, trimmed_file_name])


    # ##########################################################################
    # This conditional statement determines the form of the user passed output
    # directory, so that the "python_file_name" can be correctly appended
    # for later reference.
    #
    # TODO: Find a cleaner way to go about the first "if" clause.
    # ##########################################################################

    py_path = output_dir + "/" + parsed_grc.python_file_name
    tmp_path = output_dir + "/" + temp_file_name
    trim_path = output_dir + "/" + trimmed_file_name

    pf = PythonFormatter(py_path, tmp_path, trim_path)
    pf.format()

    # ##########################################################################
    # TODO: Write description for XML creation stage using appropriate language
    # ##########################################################################

    trimmed_grc_name = grc_name.split(".")[0]                                   # Consider changing this name since it may get confusing


    # ##########################################################################
    # TODO: THIS IS HARDCODED FOR TESTING AND WILL NEED TO BE CHANGEd!!!!!!!!!!!
    # ##########################################################################
    generator = "python.component.gr_flowgraph"
    # old_generator = "python.component.pull"

    respkg = cx.main(trimmed_grc_name, "python", output_dir,
        generator, parsed_grc.properties_array,
        parsed_grc.source_types, parsed_grc.sink_types, grc_input, py_path)

    jfe.main(respkg["rp"].autotoolsDir, parsed_grc.python_file_name, trimmed_grc_name, parsed_grc.properties_array, respkg["rp"], respkg["pd"])

    respkg["rp"].callCodegen(force=True) #Generates remaining nescessary files

    subprocess.call(["mv", py_path, respkg["rp"].autotoolsDir])

    # ##########################################################################
    # TODO: Consider placing the XML creation before the python file creation
    #       and formatting so that we can avoid the unnescessary moving of the
    #       python file into the xml/python folder, and just have it created
    #       there from the beginning. CANNOT MOVE UNLESS callCodegen() WAS
    #       CALLED!
    #       < xml_dir = output_dir + "/" + trimmed_grc_name + "/python" >
    #       < subprocess.call(["mv", py_path, xml_dir]) >
    # ##########################################################################

if __name__ == '__main__':
    main()
