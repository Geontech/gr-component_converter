#!/usr/bin/env python2

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

# ##############################################################################
# These regexps will be used to completely remove sections/lines of the
# given python file without replacing.
# ##############################################################################
regexp = []
regexp.append(re.compile(r"if __name__ == '__main__':.*print \"Warning: failed to XInitThreads\(\)\"", re.S))
regexp.append(re.compile(r"from PyQt4 import Qt"))
regexp.append(re.compile(r"import sys"))
regexp.append(re.compile(r"from gnuradio import qtgui"))
regexp.append(re.compile(r"\s*Qt.QWidget.__init__\(self\).*self.restoreGeometry\(self.settings.value\(\"geometry\"\).toByteArray\(\)\)", re.S))
regexp.append(re.compile(r"\s*def closeEvent\(self, event\):.*event.accept\(\)", re.S))
regexp.append(re.compile(r"\s*from distutils.version import StrictVersion.*qapp = Qt.QApplication\(sys\.argv\)", re.S))
regexp.append(re.compile(r"\s*def quitting\(\):.*qapp.exec_\(\)", re.S))
total_len = len(regexp)

# ##############################################################################
# Here I defined a namedTuple type that contains the regular expression to
# search for, and the string that it will be replaced with. I also defined an
# array to store and easily iterate over the tuples once nescessary.
# ##############################################################################
subarr = []
Sub = namedtuple("SubPair", "match replacement")
subarr.append(Sub(match=r"class top_block\(.*\):", replacement="class top_block(gr.top_block):"))
subarr.append(Sub(match=r"def __init__\(.*\):", replacement="def __init__(self, naming_context_ior, corba_namespace_name):"))
subarr.append(Sub(match=r"self.redhawk_integration_redhawk_source_([0-9]+) = redhawk_integration_python.redhawk_source\('', '', (.*), (.*)\)",
    replacement=None))
subarr.append(Sub(match=r"self.redhawk_integration_redhawk_sink_([0-9]+) = redhawk_integration_python.redhawk_sink\('', '', (.*)\)",
    replacement=None))
# subarr.append(Sub(match=r"self.redhawk_integration_redhawk_source_0 = redhawk_integration_python.redhawk_source\('', '',",
#     replacement="self.redhawk_integration_redhawk_source_0 = redhawk_integration_python.redhawk_source( naming_context_ior, corba_namespace_name,"))
# subarr.append(Sub(match=r"self.redhawk_integration_redhawk_sink_0 = redhawk_integration_python.redhawk_sink\('', '',",
#     replacement="self.redhawk_integration_redhawk_sink_0 = redhawk_integration_python.redhawk_sink( naming_context_ior, corba_namespace_name,"))
subarr.append(Sub(match=r"tb.show\(\)", replacement="tb.wait()"))

class PythonFormatter(object):

    def __init__(self, python_file_path, temp_file_name, trimmed_file_name):
        self.pfp = python_file_path
        self.temp = temp_file_name
        self.trimmed = trimmed_file_name

    def format(self):

        in_string = ""
        out_string = ""

        with open(self.pfp, "r") as input_file:

            in_string = input_file.read()
            comp_string = in_string

        # ######################################################################
        # This for loop iterates through the first list of regexps, matches them
        # to a string extraction of the GRC generated python file, then replaces
        # all matches with newlines which are later trimmed by an auxilary
        # method (since I don't believe you can simply substitute empty strings)
        # ######################################################################
        for expression in regexp:

            in_string = re.sub(expression, "\n", in_string)

            if self.changed(in_string, comp_string):
                comp_string = in_string
            else:
                sys.exit("Error: Incorrect GNU Radio Flowgraph format. Please refer to documentation for FG specifications.")


        # ######################################################################
        # This for loop iterates through the second set of regular expressions
        # and replaces the matches with similar strings of the correct format.
        # To account for the possibility of multiple source or sink blocks
        # being present within any given FlowGraph, I added conditional
        # statements within the loop to hold the current search position, then
        # iterate a second time through the same file string looking exclusively
        # for the source/sink block code. This is nescessary because for better
        # or for worse, the regular expression replacements are set up to be
        # executed linearly since the generated files follow a general format.
        # ######################################################################
        for pair in subarr:

            if "source" in pair.match:
                s = re.search(pair[0], in_string)
                in_string = re.sub(pair[0], self.sourcerepl(s), in_string)
            elif "sink" in pair.match:
                s = re.search(pair[0], in_string)
                in_string = re.sub(pair[0], self.sinkrepl, in_string)
            else:
                in_string = re.sub(pair[0], pair[1], in_string)

            if self.changed(in_string, comp_string):
                comp_string = in_string
            else:
                sys.exit("Error: Incorrect GNU Radio Flowgraph format. Please refer to documentation for FG specifications.")

        with open(self.temp, "w") as output_file:

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
    # Simply determines if the regular expression substitution succeeded or not.
    # If not, "False" will be returned, and the main format() function will
    # throw a error that describes the incorrect situation it has encountered.
    # ##########################################################################
    def changed(self, in_string, comp_string):

        if in_string == comp_string:
            return False
        else:
            return True


#   replacement="self.redhawk_integration_redhawk_sink_0 = redhawk_integration_python.redhawk_sink( naming_context_ior, corba_namespace_name,"))
    def sourcerepl(self, matchobj):
        return "self.redhawk_integration_redhawk_source_" + matchobj.group(1) + " = redhawk_integration_python.redhawk_source( naming_context_ior, corba_namespace_name, " + matchobj.group(2) + ", " + matchobj.group(3) + ")"

    def sinkrepl(self, matchobj):
        return "self.redhawk_integration_redhawk_sink_" + matchobj.group(1) + " = redhawk_integration_python.redhawk_sink( naming_context_ior, corba_namespace_name, " + matchobj.group(2) + ")"


    # ##########################################################################
    # Removes excessive white-space lines created by the regular expression
    # substitution method in format().
    # ##########################################################################
    def trim_blank_lines(self):

        with open(self.trimmed, "w") as output_file, open(self.temp, "r") as iter_file:

            first_space = True

            for line in iter_file:
                if not line.isspace():
                    output_file.write(line)
                    first_space = True
                else:
                    if first_space:
                        output_file.write("\n")
                        first_space = False
