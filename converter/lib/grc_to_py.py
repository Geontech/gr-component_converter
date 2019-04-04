import os
from gnuradio import gr
try:
    from grc.core.Platform import Platform
except ImportError:
    from gnuradio.grc.core.Platform import Platform

def grc_to_py(grcfile, outdir):
    platform = Platform(
        prefs_file=gr.prefs(),
        version=gr.version(),
        version_parts=(gr.major_version(), gr.api_version(), gr.minor_version())
    )
    data = platform.parse_flow_graph(grcfile)

    # Clean out the QT GUI, etc.
    blocks = data['flow_graph']['block']
    for b in blocks:
        if b['key'] == 'options':
            for opt in b['param']:
                if opt['key'] == 'generate_options' and opt['value'] != 'no_gui':
                    opt['value'] = 'no_gui'
                elif opt['key'] == 'run_options' and opt['value'] != 'run':
                    opt['value'] = 'run'
                elif opt['key'] == 'run' and opt['value'] != 'False':
                    opt['value'] = 'False'

    fg = platform.get_new_flow_graph()
    fg.import_data(data)
    fg.grc_file_path = os.path.abspath(grcfile)
    fg.validate()

    if not fg.is_valid():
        raise StandardError("\n\n".join(
            ["Validation failed:"] + fg.get_error_messages()
        ))

    if outdir[-1] != '/':
        outdir += '/'
    gen = platform.Generator(fg, outdir)
    gen.write()
