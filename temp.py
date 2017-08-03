#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Top Block
# Generated: Wed Aug  2 14:41:39 2017
##################################################

from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from optparse import OptionParser
import redhawk_integration_python

class top_block(gr.top_block):

    def __init__(self, naming_context_ior, corba_namespace_name):
        gr.top_block.__init__(self, "Top Block")

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 32000
        self.multiplier = multiplier = 2

        ##################################################
        # Blocks
        ##################################################
        self.redhawk_integration_redhawk_source_2 = redhawk_integration_python.redhawk_source('', '', "float", 10)
        self.redhawk_integration_redhawk_source_1 = redhawk_integration_python.redhawk_source('', '', "float", 10)
        self.redhawk_integration_redhawk_source_0 = redhawk_integration_python.redhawk_source( naming_context_ior, corba_namespace_name, "int", 10)
        self.redhawk_integration_redhawk_sink_0 = redhawk_integration_python.redhawk_sink( naming_context_ior, corba_namespace_name, "int")
        self.blocks_multiply_xx_1 = blocks.multiply_vii(1)
        self.blocks_multiply_xx_0 = blocks.multiply_vff(1)

        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_multiply_xx_0, 0), (self.blocks_multiply_xx_1, 0))
        self.connect((self.blocks_multiply_xx_1, 0), (self.redhawk_integration_redhawk_sink_0, 0))
        self.connect((self.redhawk_integration_redhawk_source_0, 0), (self.blocks_multiply_xx_1, 1))
        self.connect((self.redhawk_integration_redhawk_source_1, 0), (self.blocks_multiply_xx_0, 0))
        self.connect((self.redhawk_integration_redhawk_source_2, 0), (self.blocks_multiply_xx_0, 1))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate

    def get_multiplier(self):
        return self.multiplier

    def set_multiplier(self, multiplier):
        self.multiplier = multiplier

def main(top_block_cls=top_block, options=None):

    tb = top_block_cls()
    tb.start()
    tb.wait()

if __name__ == '__main__':
    main()
