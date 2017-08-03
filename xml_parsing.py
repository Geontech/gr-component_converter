#!/usr/bin/env python2

##################################################
# File: xml_parsing.py
# Author: Chris Conover
# Description: Captures vairables, source/sink
#              blocks and type information
# Created: Wed July 5 13:30:00 2017
##################################################

import re
import sys
from array import array
from collections import namedtuple
import xml.etree.ElementTree as ET
# import numpy as np

# ##############################################################################
# Other written methods for isolating values can be found in the "temp.txt" file
# ##############################################################################

GNUBlock = namedtuple("GNUBlock", "block_type name value label type ref")
RHBlock = namedtuple("RHBlock", "name type")

class XMLParsing(object):

    def __init__(self, file_name):
        self.tree = ET.parse(file_name)
        self.root = self.tree.getroot()
        self.temp_arr = []
        self.block_array = []
        self.properties_array = []
        self.first_iteration = True
        self.block_count = -1
        self.python_file_name = ""
        self.source_types = []
        self.sink_types = []
        self.io_type = ""


    # ##############################################################################
    # This method is responsible for iterating through the provided XML file and
    # identifying the block type, name, value, label, data type, and references
    # if relevent. This information is stored in a 2D array with headers based on
    # found <block>s that are not the very first block occurrance (since that first
    # block only contains setup information). Empty fields are then filled with
    # the value, "None". Then, the array is converted into the namedTuple type
    # "GNUBlock" for easy iteration, and will be used to populate xml files.
    # ##############################################################################
    def parse(self):

        for block in self.root.findall('block'):
          if self.first_iteration == False:                                     # We discount the first "block" that we find when parsing since it contains only "option" information,

              enabled = True

              gnublk = block.find('key').text                                   # Do not construct the namedTuple object if the GRC file indicates that the specific block is diabled.
              for param in block.findall('param'):
                  key = param.find('key').text
                  if key == "_enabled":
                      enabled = param.find('value').text

              if enabled == "True":

                  self.block_count += 1                                         # which is essentially the background information stored in the "top_block" block (Top left) of the FG
                  self.temp_arr.append([])
                  self.temp_arr[self.block_count].append(gnublk)

                  for i in range(0, 5):                                         # Adding blank array positions under each block header for correct insertion of attributes
                      self.temp_arr[self.block_count].append([])

                  self.temp_arr[self.block_count][5] = None                     # Default reference to None until found otherwise

                  for param in block.findall('param'):

                      key = param.find('key').text

                      if key == "id":
                          name = param.find('value').text
                          self.temp_arr[self.block_count][1] = name
                      elif key == "value" or key == "const":
                          data = param.find('value').text
                          self.temp_arr[self.block_count][2] = data
                      elif key == "label":
                          label = param.find('value').text
                          self.temp_arr[self.block_count][3] = label
                      elif key == "type":
                          d_type = param.find('value').text
                          self.temp_arr[self.block_count][4] = d_type

          else:                                                                 # On the first iteration, we only want information about the name of the python file
              for param in block.findall('param'):                              # that will be created by calling grcc on the respected .grc file (since the two don't always match).

                  key = param.find('key').text

                  if key == "id":
                      self.python_file_name = param.find('value').text + ".py"


              self.first_iteration = False

        for i in range(0, len(self.temp_arr)):

            # if self.temp_arr[i][0] == "variable":
            #     self.temp_arr[i][4] = "raw"

            # ##################################################################
            # TODO: Determine if the assignment statement below is creating
            #       references or new values. We want new values.
            # ##################################################################

            for j in range(0, len(self.temp_arr)):
                if "variable" in self.temp_arr[i][0] and (self.temp_arr[i][1] ==
                    self.temp_arr[j][2] or self.temp_arr[i][1] == self.temp_arr[j][5]):

                    self.temp_arr[i][4] = self.temp_arr[j][4]

                if self.temp_arr[i][2] == self.temp_arr[j][1]:
                    self.temp_arr[i][2] = self.temp_arr[j][2]
                    self.temp_arr[i][5] = self.temp_arr[j][1]


                    # ##########################################################
                    # Optional numpy implementation if we end up not wanting
                    # to be assigning pointers, but copied values instead.
                    #
                    # self.temp_arr[i][2] = np.array(self.temp_arr)[[j], [2]]
                    # self.temp_arr[i][5] = np.array(self.temp_arr)[[j], [1]]
                    # ##########################################################

            for k in range(0, len(self.temp_arr[j])):
                if not self.temp_arr[i][k]:                                     # Replace empty list indexes ([]) with the None value
                    self.temp_arr[i][k] = None

            gnub = GNUBlock(block_type=self.temp_arr[i][0],                     # Constructing the namedTuple "GNUBlock" (defined above) from our created array
                name=self.temp_arr[i][1], value=self.temp_arr[i][2],
                label=self.temp_arr[i][3], type=self.temp_arr[i][4],
                ref=self.temp_arr[i][5])

            self.block_array.append(gnub)

    # ##########################################################################
    # In this method, the namedTuple array (created by the above parse() method)
    # is iterated through to first find all "variable" type blocks. After a
    # "variable" block is found, the method then iterates through the same
    # namedTuple array a second time to determine if the block's name is
    # referenced by another block (and used as its value). If a variable is
    # found to be referenced by another block, it is added to the
    # properties_array class variable for later use in generating
    # SimpleProperties for the generated PRF file.
    #
    # TODO: Determine if a sixth property should be added to the namedTuple to
    #       display a list of blocks that reference the current.
    #
    # TODO: Determine if we need to account for nested references of variable.
    #       I assume that we will need to...
    # ##########################################################################
    def create_properties_array(self):

        for block in self.block_array:
            if "variable" in block.block_type:

                for copy_block in self.block_array:
                    if copy_block.ref != None and block.name in copy_block.ref:
                        self.properties_array.append(block)

    # ##########################################################################
    # This method iterates through the current object's created "block_array"
    # searching for redhawk source and sink blocks. When found, select
    # information from these blocks are stored in a namedTuple and ultimately a
    # class list (in case of multiple instances). The new list is then analyzed
    # to determine the input/output "type" of the user's flowgraph and if the
    # provided flowgraph meets one input/output requirement.
    #
    # TODO: Determine if multiple REDHAWK sink blocks are valid. # YES
    #
    # TODO: How do we account for blocks that exist, and make connections in
    #       the user's passed FG, but may be currently "disabled". # Look at GRC
    #
    # TODO: In regards to above, should we give users the opportunity to
    #       enable and disable blocks on the fly? # No
    # ##########################################################################
    def find_inout_types(self):

        for block in self.block_array:
            if "redhawk_integration_redhawk_source" == block.block_type:
                self.source_types.append(RHBlock(name=block.name, type=block.type))
            elif "redhawk_integration_redhawk_sink" == block.block_type:
                self.sink_types.append(RHBlock(name=block.name, type=block.type))

        if not self.source_types and not self.sink_types:
            sys.exit("No REDHAWK source or sink block provided. Exiting.")
        elif not self.source_types:
            self.io_type = "sink only"
        elif not self.sink_types:
            self.io_type = "source only"
        else:
            self.io_type = "source and sink"

    # ##########################################################################
    # This method was added to provide quick testing capabilities for data
    # extraction from a user passed GRC file. Once the XMLParsing object is
    # created and XMLParsing.testing() is called, this method calls upon upon
    # all of the other methods in this class and outputs all relevent
    # information to a file named "testing_output.txt" in the current directory.
    # ##########################################################################
    def testing(self):

        self.parse()
        self.create_properties_array()
        self.find_inout_types()

        f = open("testing_output.txt", "w")
        f.write("Output from iterating over current objects \"block_array\": \n")

        for block in self.block_array:
            f.write(str(block) + "\n")

        if self.properties_array:
            f.write("\nContents of the \"properties_array\" list: \n")
            for block in self.properties_array:
                f.write(str(block) + "\n")

        if self.source_types:
            f.write("\nContents of \"source_types\" list: \n")
            for item in self.source_types:
                f.write(str(item) + "\n")

        if self.sink_types:
            f.write("\nContents of \"sink_types\" list: \n")
            for item in self.sink_types:
                f.write(str(item) + "\n")

        if self.io_type:
            f.write("\nInput/output type of flow graph: ")
            f.write(self.io_type)

        f.close()
