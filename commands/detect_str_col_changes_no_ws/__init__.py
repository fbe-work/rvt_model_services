import rjm
import os.path as op
from . import data_handler


def cmd_journal(project_code, model_path, jrn_path, com_dir, log_dir):
    op.basename(op.dirname(__file__))
    coo_qc_dir = op.join(com_dir, op.basename(op.dirname(__file__)))
    rvt_jrn = rjm.JournalMaker()
    com_data = {
        "SearchPaths": coo_qc_dir,
        "ModelName": op.basename(model_path),
        "OutputPath": log_dir,
        "OutputPrefix": project_code,
        "LogFile": op.join(log_dir, "rms_exec_results.log"),
        "ScriptSource": op.join(coo_qc_dir, "rps_str_col_data_dump.py"),
    }
    rvt_jrn.execute_command(
        tab_name='Add-Ins',
        panel_name='  Revit Model Services (RMS)  ',
        command_module='RMSCmdExecutor',
        command_class='RMSCmdExecutorCommand',
        command_data=com_data,
    )
    rvt_jrn.close_model()
    rvt_jrn.write_journal(jrn_path)


register = {
    "name": "detect_str_col_changes_no_ws",
    "rjm": cmd_journal,
    "post_process": {"func": data_handler.data_pickup_and_compare,
                     "args": ["project_code"]},
}
