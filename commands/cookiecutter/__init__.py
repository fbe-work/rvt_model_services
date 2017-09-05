import rjm
import os.path as op
from . import cookie


def cmd_journal(project_code, model_path, jrn_path, com_dir, log_dir):
    op.basename(op.dirname(__file__))
    coo_qc_dir = op.join(com_dir, op.basename(op.dirname(__file__)))
    rvt_jrn = rjm.JournalMaker()
    rvt_jrn.open_workshared_model(model_path=model_path, detached=True, audit=True)
    com_data = {"SearchPaths": coo_qc_dir,
                "ModelName": op.basename(model_path),
                "OutputPath": log_dir,
                "OutputPrefix": project_code,
                "LogFile": op.join(log_dir, "rms_exec_results.log"),
                "ScriptSource": op.join(coo_qc_dir, "rps_cookie.py"),
                }
    rvt_jrn.execute_command(tab_name='Add-Ins',
                            panel_name='  Revit Model Services (RMS)  ',
                            command_module='RMSCmdExecutor',
                            command_class='RMSCmdExecutorCommand',
                            command_data=com_data,
                            )
    rvt_jrn.close_model()
    rvt_jrn.write_journal(jrn_path)


register = {"name": "cookiecutter",
            "post_process": {"func": cookie.says_hi,
                             "args": ["project_code"]},
            "rjm": cmd_journal,
            }
