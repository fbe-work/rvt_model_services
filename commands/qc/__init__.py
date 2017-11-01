import rjm
import os.path as op
from . import bokeh_qc_graphs


def cmd_journal(project_code, model_path, jrn_path, com_dir, log_dir):
    com_qc_dir = op.join(com_dir, op.basename(op.dirname(__file__)))
    rvt_jrn = rjm.JournalMaker(permissive=False)
    rvt_jrn.open_workshared_model(model_path=model_path, detached=True, audit=True)
    com_data = {"SearchPaths": com_qc_dir,
                "ModelName": op.basename(model_path),
                "OutputPath": log_dir,
                "OutputPrefix": project_code,
                "LogFile": op.join(log_dir, "rms_exec_results.log"),
                "ScriptSource": op.join(com_qc_dir, "rps_qc_model.py"),
                }
    rvt_jrn.execute_command(tab_name='Add-Ins',
                            panel_name='  Revit Model Services (RMS)  ',
                            command_module='RMSCmdExecutor',
                            command_class='RMSCmdExecutorCommand',
                            command_data=com_data,
                            )
    rvt_jrn.close_model()
    rvt_jrn.write_journal(jrn_path)


register = {"name": "qc",
            "post_process": {"func": bokeh_qc_graphs.update_graphs,
                             "args": ["project_code", "html_path"]},
            "rjm": cmd_journal,
            }
