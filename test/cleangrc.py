import os
from gnuradio.grc.python.Platform import Platform

def cleangrc(grcfile):
    platform = Platform()
    data = platform.parse_flow_graph(grcfile)

    # Clean out the QT GUI
    blocks = data['flow_graph']['block']
    for b in blocks:
        if b['key'] == 'options':
            for opt in b['param']:
                if opt['key'] == 'generate_options' and opt['value'] != 'no_gui':
                    #_log.warn('Overriding generate_options to No-GUI')
                    opt['value'] = 'no_gui'
                elif opt['key'] == 'run_options' and opt['value'] != 'run':
                    #_log.warn('Overriding run_options to RUN')
                    opt['value'] = 'run'
                elif opt['key'] == 'run' and opt['value'] != 'False':
                    #_log.warn('Overriding run to False')
                    opt['value'] = 'False'

    fg = platform.get_new_flow_graph()
    fg.import_data(data)
    fg.grc_file_path = os.path.abspath(grcfile)
    fg.validate()

    if not fg.is_valid():
        raise StandardError("\n\n".join(
            ["Validation failed:"] + fg.get_error_messages()
        ))

    return platform, fg, data