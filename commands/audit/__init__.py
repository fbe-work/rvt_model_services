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

register = {"name": "audit",
            "override_jrn_template": override_jrn_template,
            }
