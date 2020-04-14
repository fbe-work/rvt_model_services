import os
import os.path as op
import clr
clr.AddReference("RevitAPI")
from Autodesk.Revit.DB import OpenOptions, DetachFromCentralOption, FilePath
from Autodesk.Revit.DB import WorksetConfiguration, WorksetConfigurationOption
from Autodesk.Revit.DB import BuiltInCategory as Bic
import rps_data_dump


app = __revit__.Application

project = os.environ["RVT_QC_PRJ"]
model_path = os.environ["RVT_QC_PATH"]

dd_command_path = op.dirname(op.abspath(__file__))
COMMANDS_DIR = op.dirname(dd_command_path)
ROOT = op.dirname(COMMANDS_DIR)
DATA_DUMP_PATH = op.join(ROOT, "data_dumps")

rvt_path = FilePath(model_path)

ws_conf = WorksetConfiguration(WorksetConfigurationOption.CloseAllWorksets)
open_opt = OpenOptions()
open_opt.Audit = True
open_opt.DetachFromCentralOption = DetachFromCentralOption.DetachAndPreserveWorksets
open_opt.SetOpenWorksetsConfiguration(ws_conf)

no_ui_doc = app.OpenDocumentFile(rvt_path, open_opt)
print("{} - {}".format(project, model_path))

doc = no_ui_doc

rps_data_dump.dump(
    doc,
    typed_categories=[Bic.OST_StructuralColumns],
    export_path=DATA_DUMP_PATH,
)
