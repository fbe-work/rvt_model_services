import datetime
import rjm
from pathlib import Path
from . import cookie


def cmd_journal(project_code, model_path, jrn_path, com_dir, log_dir):
    command_path = Path(__file__).parent
    command_name = command_path.name
    time_stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    rvt_jrn = rjm.JournalMaker()
    rvt_jrn.open_workshared_model(model_path=model_path, detached=True, audit=True)
    rvt_jrn.add_custom_entry(override_jrn_command.format(project_code))
    com_data = {
        "SearchPaths": command_path,
        "ModelName": model_path.name,
        "OutputPath": log_dir,
        "OutputPrefix": project_code,
        "LogFile": log_dir / f"{time_stamp}_{command_name}_rms_exec_results.log",
        "ScriptSource": command_path / "rps_cookie.py",
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


override_jrn_command = """' A template to extend with journal functionality for project: {0}"""

register = {
    "name": "cookiecutter",
    "post_process": {"func": cookie.says_hi,
                     "args": ["project_code"]},
    "rjm": cmd_journal,
}
