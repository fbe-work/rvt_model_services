import rjm
import os.path as op
from . import cookie


def cmd_journal(project_code, model_path, jrn_path, com_dir, log_dir):
    op.basename(op.dirname(__file__))
    coo_qc_dir = op.join(com_dir, op.basename(op.dirname(__file__)))
    jrn_path = "d:/delme/{0}".format(project_code + ".txt")  # delme temporary deviation
    rvt_jrn = rjm.JournalMaker()
    rvt_jrn.open_workshared_model(model_path=model_path,
                                  detached=True,
                                  audit=True
                                  )
    com_data = {"SearchPaths": coo_qc_dir,
                "ModelName": op.basename(model_path),
                "OutputPath": log_dir,
                "OutputPrefix": "Session_prefix_",
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


override_jrn_template = """' 0:< 'C 27-Oct-2016 19:33:31.459;
Dim Jrn
Set Jrn = CrsJournalScript
 Jrn.Command "Internal" , "Show or hide recent files , ID_STARTUP_PAGE"
 Jrn.Command "Internal" , "Open an existing project , ID_REVIT_FILE_OPEN"
 Jrn.Data "FileOpenSubDialog" , "OpenAsLocalCheckBox", "True"
 Jrn.Data "FileOpenSubDialog" , "DetachCheckBox", "True"
 Jrn.Data "FileOpenSubDialog" , "OpenAsLocalCheckBox", "False"
 Jrn.Data "FileOpenSubDialog"  , "AuditCheckBox", "True"
 Jrn.Data "TaskDialogResult" , "This operation can take a long time. Recommended use includes periodic maintenance of large files and preparation for upgrading to a new release. Do you want to continue?",  "Yes", "IDYES"
 Jrn.Data "File Name" , "IDOK",{0}
 Jrn.Data "WorksetConfig" , "Custom", 0
 Jrn.Data "TaskDialogResult" , "Detaching this model will create an independent model. You will be unable to synchronize your changes with the original central model." & vbLf & "What do you want to do?", "Detach and preserve worksets", "1001"
 Jrn.Directive "DocSymbol" , "[]"{1}
 Jrn.Command "SystemMenu" , "Quit the application; prompts to save projects , ID_APP_EXIT"
 Jrn.Data "TaskDialogResult" , "Do you want to save changes to Untitled?", "No", "IDNO"
 """

override_addin_template = """<?xml version="1.0" encoding="utf-16" standalone="no"?>
<RevitAddIns>
  <AddIn Type="Application">
    <Name>RevitPythonShell</Name>
    <Assembly>C:\Program Files (x86)\RevitPythonShell{0}\RevitPythonShell.dll</Assembly>
    <AddInId>3a7a1d24-51ed-462b-949f-1ddcca12008d</AddInId>
    <FullClassName>RevitPythonShell.RevitPythonShellApplication</FullClassName>
  <VendorId>RIPS</VendorId>
  </AddIn>
</RevitAddIns>

"""


register = {"name": "cookiecutter",
            "override_jrn_template": override_jrn_template,
            "override_addin_template": override_addin_template,
            "post_process": {"func": cookie.says_hi,
                             "args": ["project_code"]},
            "rjm": cmd_journal,
            }
