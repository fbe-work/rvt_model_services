import os
import clr
clr.AddReference("RevitAPI")
from Autodesk.Revit.DB import OpenOptions, DetachFromCentralOption, FilePath

app = __revit__.Application
open_opt = OpenOptions()
open_opt.Audit = True
open_opt.DetachFromCentralOption = DetachFromCentralOption.DetachAndPreserveWorksets

if "RVT_QC_PRJ" not in os.environ:
    print("no model specified")

else:
    project = os.environ["RVT_QC_PRJ"]
    model_path = os.environ["RVT_QC_PATH"]

    rvt_path = FilePath(model_path)
    app.OpenDocumentFile(rvt_path, open_opt)
    # print("{} - {}".format(project, model_path))
