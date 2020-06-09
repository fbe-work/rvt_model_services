import datetime
import rjm
from pathlib import Path
import os
import psutil


def cmd_journal(project_code, model_path, jrn_path, com_dir, log_dir):
    command_path = Path(__file__).parent
    command_name = command_path.name
    time_stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    rvt_jrn = rjm.JournalMaker()
    com_data = {
        "SearchPaths": command_path,
        "ModelName": model_path.name,
        "OutputPath": log_dir,
        "OutputPrefix": project_code,
        "LogFile": log_dir / f"{time_stamp}_{command_name}_rms_exec_results.log",
        "ScriptSource": command_path / "rps_detach_audit.py",
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
    rvt_jrn.exit()


pc_stats = ""
pc_stats += f"{os.environ.get('COMPUTERNAME')};"
pc_stats += f"cores:{psutil.cpu_count()};"
pc_stats += f"cpu_mhz:{psutil.cpu_freq().current} of {psutil.cpu_freq().max};"
pc_stats += f"RAM:{psutil.virtual_memory().percent}%_used_of_{round(psutil.virtual_memory().total / 1024 ** 3)}GB;"
os.environ["pc_stats"] = pc_stats
register = {
    "name": "sync_benchmark",
    "rjm": cmd_journal,
}
