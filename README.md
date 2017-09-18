# GRC to REDHAWK Component Converter

This tool ingests a GNURadio Flow Graph (GRC XML) and outputs a custom REHDAWK Component capable of representing variables and data stream ports using Properties and BULKIO Ports, respectively.  The Component can then be included in an arbitrary Waveform and deployed into a network-distributed REDHAWK Domain.

## Flow Graph Requirements

1. Remove and/or disable all UI elements from the Flow Graph.  If you **must** have a display output for a data stream, consider using a `redhawk_sink` block and the plotting capabilities in REDHAWK SDR's IDE or using a web-based solution such as Geon's [REST-Python][rest-python] or REDHAWK SDR's [Enterprise Integration][rei] and a suitable web UI front end.

2. Replace any hardware-specific blocks for data ingress and egress with `redhawk_source` and `redhawk_sink` blocks.

## Tool Requirements

This tool requires that all of the following be installed wherever this tool is run:

 1. REDHAWK SDR 2.0.6
 2. GNURadio 3.7.9
 3. [GNURadio REDHAWK Integration Python][gr-rip]

## Installation

Install the `gr_flowgraph` REDHAWK Component Template using the associated Makefile:

```
sudo make install
```

This will load the template into the `OSSIEHOME` Python package for the REDHAWK SDR Code Generator.

## Usage

Assuming your Flow Graph has been configured to [meet the requirements](#flow-graph-requirements), conversion to a REDHAWK Component project is a single step:

```
./converter/run.py ./path_to/my_flowgraph.grc [./path_to_component]
```

The location where to store the Component definition is optional; its default is the current working directory.

 > **Pybombs Users:** Source your `setup_env.sh` script before running the converter as it requires `PYTHON_PATH` to include your GNURadio installation.

## Deployment

You can then deploy (install) the Component to the `SDRROOT` as one would any typical REDHAWK Component:

```
cd COMPONENT_DIRECTORY
./build.sh
./build.sh install
```

 > **Note:** The above assumes that the user running the commands is a member of the `redhawk` group so that the user has write access to the `SDRROOT`.

 > **Important:** The above depends extensively on your deployment scheme.  See the [GNURadio REDHAWK][gr-rh] project for more information.


[gr-rh]:       https://github.com/GeonTech/gnuradio-redhawk
[gr-rip]:      https://github.com/GeonTech/gr-redhawk_integration_python
[rest-python]: https://github.com/GeonTech/rest-python
[rei]:         https://github.com/RedhawkSDR/enterprise
