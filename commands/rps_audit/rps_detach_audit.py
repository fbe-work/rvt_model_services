import os
import sys
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
    try:
        app.OpenDocumentFile(rvt_path, open_opt)
        # print("{} - {}".format(project, model_path))
    except:
        # added for models with a specific familiy corruption blocking hte check
        print("loading model {} failed".format(rvt_path))
        sys.exit()
