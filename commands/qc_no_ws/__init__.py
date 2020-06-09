import datetime
import rjm
from pathlib import Path
from . import bokeh_qc_graphs


def cmd_journal(project_code, model_path, jrn_path, com_dir, log_dir):
    command_path = Path(__file__).parent
    command_name = command_path.name
    time_stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    rvt_jrn = rjm.JournalMaker(permissive=False)
    com_data = {
        "SearchPaths": command_path,
        "ModelName": model_path.name,
        "OutputPath": log_dir,
        "OutputPrefix": project_code,
        "LogFile": log_dir / f"{time_stamp}_{command_name}_rms_exec_results.log",
        "ScriptSource": command_path / "rps_detach_audit_qc.py",

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
    "name": "qc_no_ws",
    "post_process": {"func": bokeh_qc_graphs.update_graphs,
                     "args": ["project_code", "html_path"]},
    "rjm": cmd_journal,
}
