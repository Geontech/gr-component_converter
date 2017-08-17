##################################################
# File: python_formatter.py
# Author: Chris Conover
# Description: Takes the produced python file
#              and performs regexp substitutions
#              to format them appropriately
# Created: Wed July 13 10:00:00 2017
##################################################

# ##############################################################################
# I know for a fact that this formatter works with the following run options:
# "./run.py ../grc_files/copy_mult_pass.grc ../generated_files/" and was
# designed specifically with this example in mind.
#
# TODO: Make sure that the regexps still match the correct lines in a
#       generated python file that is not from the above GRC file.
# ##############################################################################

# ##############################################################################
# This file will get called by "run.py" after the shell script has generated
# the python file (via. "grcc") from the user passed GRC file, in order to
# format it in the way we would like. By default, "grcc" generates a python file
# that contains both unnescessary and incorrect code for our specific
# implementation desires, so this file utilizes python's regexp library to
# remove and replace some of this undesired code with functional code. The
# first for loop of regexps will simply remove excess code from the py file, and
# the second will be concerned with replacing things such as parameters that are
# incorrect by default. The file is then subject to the trim_blank_lines method
# which will remove extra spaces for more user-friendly viewing.
# ##############################################################################

# TODO: Determine if all regexps in the second set allow for different user
#       defined block options (type, rate, etc.) instead of overwriting them

# TODO: Determine if I need to account for a python file passed in that has
#       already been correctly formatted to our desires/requirements.

# TODO: Try to anticipate the ways that a provided python file may not get
#       matched by my fairly particular set of regualar expressions.

# TODO: Determine if it is alright to have multiple subprocess statements in the
#       same overarching script (with different files)?

# TODO: Is there a more efficient/professional way to be going about this?

# TODO: Rethink the fail condition. I'm not sure that every generated python
#       file is going to require exactly every change that has been considered
#       for the basic const_mult style flowgraph.

import re
import sys
import subprocess
from collections import namedtuple


class PythonFormatter(object):

    def __init__(self, python_file_path, temp_file_name, trimmed_file_name):
        self.pfp = python_file_path
        self.temp = temp_file_name
        self.trimmed = trimmed_file_name

    def format(self):
        # ##############################################################################
        # Here I defined a namedTuple type that contains the regular expression to
        # search for, and the string that it will be replaced with. I also defined an
        # array to store and easily iterate over the tuples once nescessary.
        # ##############################################################################
        subarr = []
        Sub = namedtuple("SubPair", "match replacement")
        subarr.append(Sub(match=r"class top_block\(.*\):", replacement="class top_block(gr.top_block):"))
        subarr.append(Sub(match=r"def __init__\(.*\):", replacement="def __init__(self, naming_context_ior, corba_namespace_name):"))

        in_string = ""
        with open(self.pfp, "r") as input_file:
            in_string = input_file.read()
            comp_string = in_string

        # ######################################################################
        # This for loop iterates through the second set of regular expressions
        # and replaces the matches with similar strings of the correct format.
        # To account for the possibility of multiple source or sink blocks
        # being present within any given FlowGraph, I implemented helper
        # functions for the built in re.sub method, which will search for
        # all occurances of my specified string within the file's text, and
        # call the helper method for each occurrance found. The helper methods
        # then simply format the captured regular expression groups how we would
        # like, and return them to be substituted back into the file's text.
        # ######################################################################
        for pair in subarr:
            in_string = re.sub(pair[0], pair[1], in_string)

            if in_string != comp_string:
                comp_string = in_string
            else:
                # FIXME: make this a log message
                print "Skipped substitution for: {0}".format(pair[0])
                # sys.exit("Error: Incorrect GNU Radio Flowgraph format. Please refer to documentation for FG specifications.")

        with open(self.temp, "w+") as output_file:
            output_file.write(in_string)

        self.trim_blank_lines()

        # ######################################################################
        # Copying the correct final output (located in the _trimmed file) to
        # the respected .py file, and removing the associated temporary files.
        # ######################################################################
        subprocess.call(["cp", self.trimmed, self.pfp])
        subprocess.call(["rm", self.temp])
        subprocess.call(["rm", self.trimmed])

    # ##########################################################################
    # Removes excessive white-space lines created by the regular expression
    # substitution method in format().
    # ##########################################################################
    def trim_blank_lines(self):

        with open(self.trimmed, "w+") as output_file, open(self.temp, "r") as iter_file:

            first_space = True

            for line in iter_file:
                if not line.isspace():
                    output_file.write(line)
                    first_space = True
                else:
                    if first_space:
                        output_file.write("\n")
                        first_space = False
