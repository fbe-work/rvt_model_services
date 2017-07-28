from . import bokeh_qc_graphs

register = {"name": "qc",
            "get_rps_button": "qc_model",
            "optional_html_path": True,
            "post_process": {"func": bokeh_qc_graphs.update_graphs,
                             "args": ["project_code", "html_path"]},
            }
