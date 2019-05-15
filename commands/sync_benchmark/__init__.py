import rjm
import os.path as op
import os
import psutil


def cmd_journal(project_code, model_path, jrn_path, com_dir, log_dir):
    op.basename(op.dirname(__file__))
    coo_qc_dir = op.join(com_dir, op.basename(op.dirname(__file__)))
    rvt_jrn = rjm.JournalMaker()
    com_data = {"SearchPaths": coo_qc_dir,
                "ModelName": op.basename(model_path),
                "OutputPath": log_dir,
                "OutputPrefix": project_code,
                "LogFile": op.join(log_dir, "rms_exec_results.log"),
                "ScriptSource": op.join(coo_qc_dir, "rps_detach_audit.py"),
                }
    rvt_jrn.execute_command(tab_name='Add-Ins',
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
register = {"name": "sync_benchmark",
            "rjm": cmd_journal,
            }
