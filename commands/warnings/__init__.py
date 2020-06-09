import rjm
import os
from pathlib import Path
from . import bokeh_warnings_graphs


def cmd_journal(project_code, model_path, jrn_path, com_dir, log_dir):
    command_path = Path(__file__).parent
    warnings_dir = str(command_path) + os.sep
    rvt_jrn = rjm.JournalMaker()
    rvt_jrn.open_workshared_model(model_path=model_path, detached=True, audit=True)
    rvt_jrn.add_custom_entry(override_jrn_command.format(warnings_dir, project_code))
    rvt_jrn.close_model()
    rvt_jrn.write_journal(jrn_path)


override_jrn_command = """ Jrn.RibbonEvent "TabActivated:Manage"
 Jrn.Command "Ribbon" , "Review previously posted warnings , ID_REVIEW_WARNINGS"
 Jrn.Data "Error dialog" , "0 failures, 0 errors, 0 warnings"
 Jrn.PushButton "Modeless , Autodesk Revit Architecture 2016 , Dialog_Revit_ReviewWarningsDialog" _
          , "Export..., Control_Revit_ExportErrorReport"
 Jrn.Data "Error Report Action" , "IDOK"
 Jrn.Data "Error Report File Path" , "{0}"
 Jrn.Data "Error Report File Name" , "{1}"
 Jrn.Data "Error Report File Format" , "html"
 Jrn.PushButton "Modeless , Autodesk Revit Architecture 2016 , Dialog_Revit_ReviewWarningsDialog" , "Close, IDABORT"
"""

register = {
    "name": "warnings",
    "rjm": cmd_journal,
    "optional_html_path": True,
    "post_process": {"func": bokeh_warnings_graphs.update_json_and_bokeh,
                     "args": ["project_code", "html_path", "warn_ids_path"]},
}
