from . import bokeh_warnings_graphs

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

register = {"name": "warnings",
            "override_jrn_command": override_jrn_command,
            "optional_html_path": True,
            "post_process": {"func": bokeh_warnings_graphs.update_json_and_bokeh,
                             "args": ["project_code", "html_path"]},
            }
