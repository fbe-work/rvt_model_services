# -*- coding: UTF-8 -*-
"""
rvt_journal_writer
"""
import rps_xml


def write_journal(journal_file_path, journal_template, full_model_path, command):
    """
    Writes a journal to be used with revit, based on
    :param journal_file_path: journal output path.
    :param journal_template: journal template to be used as base.
    :param full_model_path: file path to the model.
    :param command: action to be performed on the model.
    :return: journal_file_path
    """
    rvt_model_file_path = '"' + full_model_path + '"'
    journal_template = journal_template.format(rvt_model_file_path, command)
    with open(journal_file_path, "w") as jrn_file:
        jrn_file.write(journal_template)
    return journal_file_path


def write_addin(addin_file_path, addin_template, rvt_version):
    """
    Writes the required *.addin to run RPS inside rvt to the journal folder
    :param addin_file_path: addin output path.
    :param addin_template: addin template to be used as base.
    :param rvt_version: rvt version to open the model with.
    :return: addin_file_path
    """
    journal_template = addin_template.format(str(rvt_version))
    with open(addin_file_path, "w") as jrn_file:
        jrn_file.write(journal_template)
    return addin_file_path


detach_rps_template = """' 0:< 'C 27-Oct-2016 19:33:31.459;
Dim Jrn
Set Jrn = CrsJournalScript
 Jrn.Command "Internal" , "Show or hide recent files , ID_STARTUP_PAGE"
 Jrn.Command "Internal" , "Open an existing project , ID_REVIT_FILE_OPEN"
 Jrn.Data "FileOpenSubDialog" , "OpenAsLocalCheckBox", "True"
 Jrn.Data "FileOpenSubDialog" , "DetachCheckBox", "True"
 Jrn.Data "FileOpenSubDialog" , "OpenAsLocalCheckBox", "False"
 Jrn.Data "File Name" , "IDOK",{0}
 Jrn.Data "WorksetConfig" , "Custom", 0
 Jrn.Data "TaskDialogResult" , "Detaching this model will create an independent model. You will be unable to synchronize your changes with the original central model." & vbLf & "What do you want to do?", "Detach and preserve worksets", "1001"
 Jrn.Directive "DocSymbol" , "[]"
 Jrn.RibbonEvent "TabActivated:Add-Ins"
 {1}
 Jrn.Command "SystemMenu" , "Quit the application; prompts to save projects , ID_APP_EXIT"
 Jrn.Data "TaskDialogResult" , "Do you want to save changes to Untitled?", "No", "IDNO"
 """

audit_detach_template = """' 0:< 'C 27-Oct-2016 19:33:31.459;
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

export_warnings_template = """ Jrn.RibbonEvent "TabActivated:Manage"
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

rps_addin_template = """<?xml version="1.0" encoding="utf-16" standalone="no"?>
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

audit = ''

if __name__ == "__main__":
    rvt_path = "N:/456_Roche-Bau-8-und-11/02_DRAWINGS/3_BASIC_DESIGN/1_OFFICIAL/BIM/01_CENTRAL/"
    rvt_file = "011_YYYY_YYY_F10_Z01.rvt"

    write_journal("D:/delme_journal_qc_test_file.txt",
                  detach_rps_template,
                  rvt_path,
                  rvt_file,
                  rps_xml.get_rps_button(rps_xml.find_xml_command("2015", ""), "qc_model"))
    write_addin("D:/delme_addin_test_file.addin",
                rps_addin_template,
                2015)
