# GRC to REDHAWK Component Converter

This tool consists of N stages that ingests a GNURadio `.grc` formatted Flow Graph and outputs a custom REHDAWK Component capable of representing variables and data stream ports using Properties and BULKIO Ports, respectively.  It assumes the GRC has had all UI elements removed and any hardware source/sink requirements have been replaced with references to the `redhawk_source` and `redhawk_sink` blocks.

1. User selects implementation type: traditional or Docker (SPD XML)
2. Transfer the list of variables (names, types) from the GRC to REDHAWK Properties (PRF XML)
3. Transfer the list of source and sink instances (and data types) from the GRC to REDHAWK BULKIO Ports (SCD XML)
4. Use REDHAWK code generator and integration template to produce the Component definition
5. Use GRC to generate the `top_block.py` of the Flow Graph and add it to the Component's sources

The Component is now ready for use with `gnuradio-redhawk` based on the selected implementation.

 > **Note:** Use of this repository requires having both REDHAWK and GNURadio installed in the same environment as these tools, as provided by `gnuradio-redhawk`, for example.

## Traditional

Traditional deployment assumes the integrator has installed GNURadio, Geon's `redhawk_integration_python` package, and all possible Flow Graph assets at every GPP in a given Domain.  This ensures the runtime deployment of the Component can utilize GNURadio and the associated integration source and sink blocks.

## Docker

Docker-based deployment of the Component requires a specialized extension to the [REDHAWK GPP](https://github.com/GeonTech/core-framework) which adds a variety of features making it Docker-aware.  It is then up to the integrator to provision the host running the GPP to have the associated Docker images installed or to expose a repository server to that host for on-the-fly pulling of images.