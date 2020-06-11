import os
import sys
import json
import clr
clr.AddReference("RevitAPI")
from Autodesk.Revit.DB import OpenOptions, DetachFromCentralOption, FilePath, ModelPathUtils
from Autodesk.Revit.DB import WorksetConfiguration, WorksetConfigurationOption
from Autodesk.Revit.DB import SaveAsOptions, WorksharingSaveAsOptions, TransmissionData

app = __revit__.Application

print(os.path.basename(__file__))

if not os.environ.get("RVT_QC_PATH"):
    print("no model specified - exiting.")
    sys.exit()

model_path = os.environ["RVT_QC_PATH"]

upgrade_dir = os.path.dirname(os.environ["RVT_QC_PATH"])
dir_files = os.listdir(upgrade_dir)

move_json_name = "move_models.json"
move_json_path = os.path.join(upgrade_dir, move_json_name)
if move_json_name not in dir_files:
    print("missing move mapping definition '{}' - exiting.".format(move_json_name))
    sys.exit()

with open(move_json_path) as json_map:
    move_models = json.load(json_map)

for model in sorted(move_models):
    if not os.path.exists(model):
        print("skipped not existing: {}".format(model))
        continue

    print(35*"-")
    model_path = model

    new_target_path = move_models.get(model)
    print("this model          : {}".format(model_path))
    print("will be saved here  : {}".format(new_target_path))

    rvt_path = FilePath(model_path)
    rvt_model_path = ModelPathUtils.ConvertUserVisiblePathToModelPath(model_path)
    print("currently processing: {}".format(model_path))

    ws_conf = WorksetConfiguration(WorksetConfigurationOption.CloseAllWorksets)
    open_opt = OpenOptions()
    open_opt.Audit = True
    open_opt.DetachFromCentralOption = DetachFromCentralOption.DetachAndPreserveWorksets
    open_opt.SetOpenWorksetsConfiguration(ws_conf)

    save_opt = SaveAsOptions()
    if os.path.exists(new_target_path):
        print("warning! overwriting: {}".format(new_target_path))
        save_opt.OverwriteExistingFile = True

    model_doc = app.OpenDocumentFile(rvt_path, open_opt)
    
    if model_doc.IsWorkshared:
        ws_opt = WorksharingSaveAsOptions()
        ws_opt.SaveAsCentral = True
        if TransmissionData.IsDocumentTransmitted(rvt_model_path):
            print("removing transmit   : {}".format(model_path))
            ws_opt.ClearTransmitted = True
        save_opt.SetWorksharingOptions(ws_opt)

    print("opened              : {}".format(model))
    model_doc.SaveAs(FilePath(new_target_path), save_opt)
    print("saved as            : {}".format(new_target_path))
    model_doc.Close()
    print("closed")

sys.exit()
